"Added image badging functionality"

from asyncio import subprocess
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory

from custom_components.custom_backend.utils import slugify


_LOGGER = getLogger(__name__)

GENERATED = "generated"

config_directory = Path("/config")
www_directory = config_directory / "www"
generated_directory = www_directory / GENERATED


async def badge_image(main, badge):
	badged_filename = f"{slugify(main)}_{slugify(badge)}.png"

	badged_destination = generated_directory / badged_filename

	if not badged_destination.exists():
		main_file_path = main.replace("/local", str(www_directory), 1)
		badge_file_path = badge.replace("/local", str(www_directory), 1)

		identify_width_command = f"identify -format %w {main_file_path}"
		width_process = await subprocess.create_subprocess_shell(
			identify_width_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
		)
		stdout, stderr = await width_process.communicate()
		if stderr:
			print(
				f"[{identify_width_command!r} exited with {width_process.returncode}]"
			)
			print(f"[stderr]\n{stderr.decode()}")

		width = int(stdout.decode("utf8"), 10)
		radius = width * 0.125

		round_main_corners_command = (
			f"convert {main_file_path} \( +clone  -alpha extract "
			f"-draw 'fill black polygon 0,0 0,{radius} {radius},0 fill white circle {radius},{radius} {radius},0' "
			"\( +clone -flip \) -compose Multiply -composite "
			"\( +clone -flop \) -compose Multiply -composite "
			f"\) -alpha off -compose CopyOpacity -composite PNG32:-"
		)

		round_main_corners_process = await subprocess.create_subprocess_shell(
			round_main_corners_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
		)
		main_rounded_stdout, stderr = await round_main_corners_process.communicate()
		if stderr:
			print(
				f"[{round_main_corners_command!r} exited with {round_main_corners_process.returncode}]"
			)
			print(f"[stderr]\n{stderr.decode()}")

		main_fraction = 0.9
		# badge_fraction = (1-main_fraction)*3
		badge_fraction = 0.5
		# shrunk_main_size = width
		shrunk_main_size = width * main_fraction
		# canvas_size = int(width/fraction)
		canvas_size = int(width)
		badge_size = int(canvas_size * badge_fraction)


		shrunk_and_placed_badge_process = await subprocess.create_subprocess_shell(
			f"convert {badge_file_path} -trim -resize {badge_size}x{badge_size} -background transparent -gravity SouthEast -extent {canvas_size}x{canvas_size} PNG32:-",
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		(
			shrunk_badge_stdout,
			stderr,
		) = await shrunk_and_placed_badge_process.communicate()

		placed_main_process = await subprocess.create_subprocess_shell(
			f"convert PNG32:- -resize {shrunk_main_size}x{shrunk_main_size} -background transparent -gravity NorthWest -extent {canvas_size}x{canvas_size} PNG32:-",
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		placed_main_stdout, stderr = await placed_main_process.communicate(
			main_rounded_stdout
		)

		cut_out_bottom_right_command = f"convert PNG32:- PNG32:-"
		cut_main_process = await subprocess.create_subprocess_shell(
			cut_out_bottom_right_command,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		cut_main_stdout, stderr = await cut_main_process.communicate(placed_main_stdout)

		with TemporaryDirectory() as td:
			new_main = Path(td) / "new-main.png"
			new_badge = Path(td) / "new-badge.png"
			with open(new_main, "wb") as new_main_file:
				new_main_file.write(cut_main_stdout)
			with open(new_badge, "wb") as new_badge_file:
				new_badge_file.write(shrunk_badge_stdout)

			badged_process = await subprocess.create_subprocess_shell(
				f"composite {new_badge} {new_main} -alpha Set PNG32:-",
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
			)
			badged_stdout, stderr = await badged_process.communicate()

		badged_destination.parent.mkdir(exist_ok=True, parents=True)
		with open(badged_destination, "wb") as out:
			out.write(badged_stdout)


	badged_path = f"/local/{GENERATED}/{badged_filename}"

	return badged_path
