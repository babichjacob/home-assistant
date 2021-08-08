import os
import sys
import yaml

from collections import OrderedDict
from copy import deepcopy
from functools import reduce

from typing import Any, List, Dict, Union
from yaml import add_constructor, load, dump, SafeLoader, YAMLError, YAMLObject
from yaml.nodes import Node
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper # type: ignore

from homeassistant.exceptions import HomeAssistantError

JSON_TYPE = Union[List, Dict, str]
SECRET_YAML = "secrets.yaml"
__SECRET_CACHE: Dict[str, JSON_TYPE] = {}

credstash = None
keyring = None
_SECRET_NAMESPACE = None

class SafeLineLoader(SafeLoader):
	"""Loader class that keeps track of line numbers."""

	def compose_node(self, parent: Node, index: int) -> Node:
		"""Annotate a node with the first line it was seen."""
		last_line: int = self.line
		node: yaml.nodes.Node = super().compose_node(parent, index)
		node.__line__ = last_line + 1  # type: ignore
		return node

def load_yaml(fname: str) -> JSON_TYPE:
	"""Load a YAML file."""
	try:
		with open(fname, encoding="utf-8") as conf_file:
			# If configuration file is empty YAML returns None
			# We convert that to an empty dict
			return load(conf_file, Loader=SafeLineLoader) or OrderedDict()
	except YAMLError as exc:
		print(str(exc))
		raise HomeAssistantError(exc)
	except UnicodeDecodeError as exc:
		print("Unable to read file %s: %s", fname, exc)
		raise HomeAssistantError(exc)

def _load_secret_yaml(secret_path: str) -> JSON_TYPE:
	"""Load the secrets yaml from path."""
	secret_path = os.path.join(secret_path, SECRET_YAML)
	if secret_path in __SECRET_CACHE:
		return __SECRET_CACHE[secret_path]

	print("Loading %s" % secret_path)
	try:
		secrets = load_yaml(secret_path)
		if not isinstance(secrets, dict):
			raise HomeAssistantError("Secrets is not a dictionary")
		if "logger" in secrets:
			logger = str(secrets["logger"]).lower()
			if logger == "debug":
				pass
			else:
				print(
					"secrets.yaml: 'logger: debug' expected, but 'logger: %s' found" % logger
				)
			del secrets["logger"]
	except FileNotFoundError:
		secrets = {}
	__SECRET_CACHE[secret_path] = secrets
	return secrets

def secret_yaml(loader: SafeLineLoader, node: Node) -> JSON_TYPE:
	"""Load secrets and embed it into the configuration YAML."""
	secret_path = os.path.dirname(loader.name)
	while True:
		secrets = _load_secret_yaml(secret_path)

		if node.value in secrets:
			print(
				"Secret %s retrieved from secrets.yaml in folder %s" % (node.value, secret_path)
			)
			return secrets[node.value]

		if secret_path == os.path.dirname(sys.path[0]):
			break  # sys.path[0] set to config/deps folder by bootstrap

		secret_path = os.path.dirname(secret_path)
		if not os.path.exists(secret_path) or len(secret_path) < 5:
			break  # Somehow we got past the .homeassistant config folder

	if keyring:
		# do some keyring stuff
		pwd = keyring.get_password(_SECRET_NAMESPACE, node.value)
		if pwd:
			print("Secret %s retrieved from keyring" % node.value)
			return pwd

	global credstash  # pylint: disable=invalid-name

	if credstash:
		# pylint: disable=no-member
		try:
			pwd = credstash.getSecret(node.value, table=_SECRET_NAMESPACE)
			if pwd:
				print("Secret %s retrieved from credstash" % node.value)
				return pwd
		except credstash.ItemNotFound:
			pass
		except Exception:  # pylint: disable=broad-except
			# Catch if package installed and no config
			credstash = None

	raise HomeAssistantError(f"Secret {node.value} not defined")

add_constructor("!secret", secret_yaml)


def merge_two(code_1, code_2):
	result = deepcopy(code_1)

	for domain, items in code_2.items():
		if isinstance(items, list):
			result.setdefault(domain, []).extend(items)
		elif isinstance(items, dict):
			result.setdefault(domain, {}).update(items)
		elif items is None:
			if result.get(domain) is not None:
				raise ValueError(f"can't merge {type(result[domain])} with None")
			else:
				result[domain] = None
		else:
			raise ValueError(f"unexpected type to merge: {type(items)}")
	
	return result


def merge(*code):
	return reduce(merge_two, code, {})
