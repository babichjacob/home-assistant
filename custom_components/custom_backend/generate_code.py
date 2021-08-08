from contextlib import ExitStack
from functools import reduce
from importlib import import_module
from os import link
from pathlib import Path
from typing import Dict, List, Optional, Union

from homeassistant import core

from . import current_directory, get_data

from .const import (
	CONF_ALIASES,
	CONF_ENTITY_CONFIG,
	CONF_EXPOSE,
	CONF_FILTER,
	CONF_INCLUDE_ENTITIES,
	CONF_NAME,
	CONF_ROOM,
	DATA_SHORT_NAME,
	DOMAIN_CUSTOM_BACKEND,
	DOMAIN_HOMEKIT,
	DOMAIN_LOCK,
	SERVICE_GENERATE_CODE,
)
from .yaml import dump, load, Loader


def deep_merge(source, destination):
	for key, value in source.items():
		if isinstance(value, dict):
			node = destination.setdefault(key, {})
			deep_merge(value, node)
		else:
			destination[key] = value



def get_corresponding_destination(generator: Path, extension: str) -> Path:
	relative = generator.relative_to(current_directory / "config")
	subdirectory = relative.parent

	destination_directory = Path(subdirectory)

	local_name = "_".join(relative.parts[1:-1])

	# Replace __init__ (unacceptable slug) with main (acceptable slug)
	generator = generator.with_name(generator.stem.replace("__init__", "main"))
	destination: Path
	if local_name:
		destination = destination_directory / \
			f"{local_name}_generated_code_{generator.stem}{extension}"
	else:
		if destination_directory.resolve() == Path("/config"):
			destination = destination_directory / f"{generator.stem}{extension}"
		else:
			destination = destination_directory / f"custom_backend_{generator.stem}{extension}"

	return destination


def clear_out_old_code_files(generators: List[Path]) -> None:
	possible_generated_code_paths = {get_corresponding_destination(
		generator, "") for generator in generators}
	possible_generated_code_directories = {
		path.parent for path in possible_generated_code_paths}

	for code_directory in possible_generated_code_directories:
		if code_directory == Path("."):
			continue

		print(f"debug: clearing out {code_directory.resolve()}")

		try:
			code_files = list(code_directory.iterdir())
		except FileNotFoundError:
			# So what, the directory doesn't exist
			pass
		else:
			for code_file in code_files:
				if code_file.with_suffix("") not in possible_generated_code_paths:
					print(f"clearing out old {code_file}")
					code_file.unlink()


def safe_unlinker(path):
	def closure():
		try:
			path.unlink()
		except FileNotFoundError:
			# Maybe it's already gone. Whatever.
			pass
	return closure


def write_code_to_disk_with_backup(*, generator: Path, code: Union[str, Dict], local_rollback: ExitStack, commit: List, extension: Optional[str] = None):
	destination = get_corresponding_destination(generator, extension)

	if extension == ".yaml":
		code_ready_to_save = dump(code)
	elif extension == ".py":
		code_ready_to_save = code
	else:
		raise ValueError(
			f"there is no known way to convert {extension} code to plain text")

	print(f"debug: writing to {destination}")

	backup = destination.with_name(f"backup_{destination.name}")
	inprog = destination.with_name(f"inprog_{destination.name}")

	destination.parent.mkdir(exist_ok=True, parents=True)

	local_rollback.callback(print, f"reverted code written to {destination}")
	local_rollback.callback(inprog.unlink)
	inprog.write_text(code_ready_to_save, encoding="utf8")

	@local_rollback.callback
	def reinstate_backup_if_it_exists():
		try:
			destination.unlink()
			link(backup, destination)
		except FileNotFoundError:
			# There was no backup to restore
			print(f"there was no backup to restore for {destination}!!!")
		else:
			backup.unlink()

	try:
		backup.unlink()
		link(destination, backup)
		destination.unlink()
	except FileNotFoundError:
		# There was nothing to back up, whatever
		pass

	try:
		destination.unlink()
	except FileNotFoundError:
		# This code has never been generated before, whatever
		pass

	link(inprog, destination)

	commit.append(safe_unlinker(inprog))


async def run_code_generator():
	data = get_data()

	generatoring_pys = list((current_directory / "config").glob("**/*.py"))

	customize = {}

	google_assistant_exposed = {}

	siri_exposed = []
	siri_entity_config = {}

	commit = []
	with ExitStack() as global_rollback:
		clear_out_old_code_files(generatoring_pys)

		for generating_py in generatoring_pys:
			if generating_py.stem.startswith("_") and generating_py.stem != "__init__":
				continue
			
			did_anything: bool = False

			import_location = generating_py.with_suffix("").relative_to(current_directory)

			imported_module = import_module(f'.{str(import_location).replace("/", ".")}', package="custom_components.custom_backend")
			
			generate_yaml = getattr(imported_module, "generate_yaml", None)
			generated_yaml = None
			if generate_yaml is not None:
				try:
					generated_yaml = await generate_yaml(**data)
				except Exception as exc:
					raise RuntimeError(
						f"code in {import_location} could not generate") from exc
				else:
					did_anything = True

			generate_customize = getattr(imported_module, "customize", None)
			generated_customize = None

			if generate_customize is not None:
				try:
					generated_customize = await generate_customize(**data)
				except Exception as exc:
					raise RuntimeError(
						f"code in {import_location} could not generate") from exc
				else:
					did_anything = True
			
			if generated_customize is not None:
				deep_merge(generated_customize, customize)
				did_anything = True

			generate_exposed_devices = getattr(imported_module, "exposed_devices", None)
			if generate_exposed_devices is not None:
				exposed_devices = generate_exposed_devices(**data)
				did_anything = True

				for entity_id, config in exposed_devices.items():
					full_name = config.get("full_name")
					names = config.get("names")

					short_name = config.get(DATA_SHORT_NAME)
					if short_name is None:
						if entity_id.startswith(f"{DOMAIN_LOCK}."):
							short_name = "Lock"

					if full_name is None:
						if names is None:
							if short_name is None:
								raise ValueError(f"`names` or `full_name` is needed for {entity_id}")
							full_name = short_name
							names = [short_name]
						full_name = names[0]
					else:
						if names is None:
							names = [full_name]

					if config.get("google_assistant", True):
						if entity_id in google_assistant_exposed:
							print(f"{entity_id} is duplicated for the Google Assistant")
						else:
							google_assistant_exposed[entity_id] = {
								CONF_NAME: full_name,
								CONF_ALIASES: names,
								**({CONF_ROOM: config["room"]} if "room" in config else {}),
								CONF_EXPOSE: True,
							}

					if config.get("siri", True):
						if entity_id in siri_exposed:
							print(f"{entity_id} is duplicated for Siri")
						else:
							siri_exposed.append(entity_id)

						entity_config = {}

						if short_name is not None:
							entity_config["name"] = short_name

						if "linked_battery_sensor" in config:
							entity_config["linked_battery_sensor"] = config["linked_battery_sensor"]

						if "code" in config:
							entity_config["code"] = config["code"]

						if entity_id.startswith("camera."):
							entity_config.update({
								"support_audio": True,
								"video_codec": "copy",
							})

						if short_name == "Radio":
							entity_config.update({
								"feature_list": [
									{
										"feature": "on_off",
									},
								],
							})

						if short_name == "TV":
							entity_config.update({
								"feature_list": [
									{
										"feature": "on_off",
									},
									{
										"feature": "play_pause",
									},
									{
										"feature": "play_stop",
									},
									{
										"feature": "toggle_mute",
									},
								],
							})

						if entity_config:
							siri_entity_config[entity_id] = entity_config

			if generated_yaml is not None:
				with ExitStack() as local_rollback:
					print(f"debug: writing yaml to disk for {generating_py}")
					write_code_to_disk_with_backup(
						generator=generating_py, code=generated_yaml, extension=".yaml", local_rollback=local_rollback, commit=commit)

					global_rollback.push(local_rollback.pop_all())

			purpose = imported_module.__doc__
			if did_anything:
				if purpose is None:
					raise RuntimeError(f"{import_location} needs to specify its purpose")
				print(f"{purpose} from {import_location}")
		else:
			# If all the code is successfully generated and written to disk, we will not roll anything back
			global_rollback.pop_all()

	for commiter in commit:
		commiter()

	commit = []

	service_account = None

	try:
		with open("/config/service_account.json") as service_account_file:
			service_account = load(service_account_file, Loader=Loader)
	except FileNotFoundError as exc:
		print()
		print(exc)
		print("Proceeding anyway (Google Assistant just won't work)")
		print()

	with ExitStack() as global_rollback:
		with ExitStack() as local_rollback:
			write_code_to_disk_with_backup(
				generator=Path("/config/custom_components/custom_backend/config/packages/custom_backend/generated_code_customize.py"), code={
					"homeassistant": {
						"customize": customize,
					}
				}, local_rollback=ExitStack(), commit=commit, extension=".yaml")

			global_rollback.push(local_rollback.pop_all())
			print("Generated code for all the entity customization ever")

		with ExitStack() as local_rollback:
			project_id = None
			try:
				project_id = data["secrets"]["google_assistant_project_id"]
			except KeyError as exc:
				print()
				print(exc)
				print("Proceeding anyway (Google Assistant just won't work)")
				print()

			if project_id is not None and service_account is not None:
				write_code_to_disk_with_backup(
					generator=Path("/config/custom_components/custom_backend/config/packages/custom_backend/generated_code_google.py"), code={
						# TODO: replace with domains and confs
						"google_assistant": {
							"project_id": project_id,
							"service_account": service_account,
							"secure_devices_pin": data["secrets"]["google_assistant_secure_device_pin"],
							"report_state": True,
							"expose_by_default": False,
							"exposed_domains": [],
							"entity_config": google_assistant_exposed,
						}
					}, local_rollback=ExitStack(), commit=commit)

				global_rollback.push(local_rollback.pop_all())
				print("Generated code for the Google Assistant")
			else:
				print("Did NOT generate code for the Google Assistant")

		with ExitStack() as local_rollback:
			write_code_to_disk_with_backup(
				generator=Path("/config/custom_components/custom_backend/config/packages/custom_backend/generated_code_siri.py"), code={
					DOMAIN_HOMEKIT: [
						{
							CONF_NAME: "Home Assistant Bridge",
							CONF_FILTER: {
								CONF_INCLUDE_ENTITIES: siri_exposed,
							},
							CONF_ENTITY_CONFIG: siri_entity_config,
						}
					]
				}, local_rollback=local_rollback, commit=commit, extension=".yaml")

			global_rollback.push(local_rollback.pop_all())
			print("Generated code for Siri")

		# If all the code is successfully generated and written to disk, we will not roll anything back
		global_rollback.pop_all()

	for commiter in commit:
		commiter()


async def async_setup(hass: core, config: Dict, **kwds):
	async def handle_generate_code(call):
		await run_code_generator()
	
	hass.services.async_register(DOMAIN_CUSTOM_BACKEND, SERVICE_GENERATE_CODE, handle_generate_code)
	return True


if __name__ == "__main__":
	from asyncio import run
	run(run_code_generator())
