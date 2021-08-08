"Registered all the cameras with the home automation and security system"

from custom_components.custom_backend.const import (
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	CONF_EXTRA_ARGUMENTS,
	CONF_INPUT,
	CONF_NAME,
	CONF_PLATFORM,
	DATA_CAMERA,
	DATA_FULL_NAME,
	DATA_GARAGE_DOORS,
	DATA_IN_VIEW,
	DATA_LIGHTS,
	DATA_LOCKS,
	DATA_NICKNAME,
	DATA_ROOM,
	DATA_STREAM_SOURCE,
	DATA_VIDEO_QUALITY,
	DATA_ZONE,
	DOMAIN_CAMERA,
	GARAGE_DOOR_GARAGE_DOOR,
	ICON_MDI_CCTV,
	LIGHT_PORCH,
	LOCK_FRONT_DOOR,
	PLATFORM_FFMPEG,
	ROOM_BACKYARD,
	ROOM_DRIVEWAY,
	ROOM_FRONT_ROOM,
	ROOM_FRONT_YARD,
	ROOM_GARAGE,
	ROOM_KITCHEN,
	ZONE_BAKA_S_HOUSE,
)
from custom_components.custom_backend.utils import slugify

async def get_cameras(**kwds):
	secrets = kwds["secrets"]

	def get_camera(slug):
		return {
			DATA_STREAM_SOURCE: secrets[f"{DATA_CAMERA}_{slug}_{DATA_STREAM_SOURCE}"],
		}

	camera_slugs = set()

	for key in secrets:
		prefix = DATA_CAMERA + "_"
		if not key.startswith(prefix):
			continue

		suffix = "_" + DATA_STREAM_SOURCE
		if not key.endswith(suffix):
			continue

		camera_slugs.add(key[len(prefix):-len(suffix)])
	
	basic_cameras = {
		camera_slug: get_camera(camera_slug) for camera_slug in camera_slugs
	}

	customizations = {
		"1": {
			DATA_IN_VIEW: {
				DATA_LIGHTS: {LIGHT_PORCH},
				DATA_LOCKS: {LOCK_FRONT_DOOR},
			},
			DATA_ROOM: ROOM_FRONT_ROOM,
		},
		"2": {
			DATA_IN_VIEW: {
				DATA_GARAGE_DOORS: {GARAGE_DOOR_GARAGE_DOOR},
			},
			DATA_ROOM: ROOM_GARAGE,
		},
		"3": {
			DATA_NICKNAME: "Gazebo",
			DATA_ROOM: ROOM_BACKYARD,
		},
		"4": {
			DATA_IN_VIEW: {
				DATA_LOCKS: {LOCK_FRONT_DOOR},
			},
			DATA_NICKNAME: "Porch",
			DATA_ROOM: ROOM_FRONT_YARD,
		},
		"5": {
			DATA_ROOM: ROOM_DRIVEWAY,
		},
		"6": {
			DATA_NICKNAME: "Fireplace",
			DATA_ROOM: ROOM_KITCHEN,
		},
		"pan_1": {
			DATA_ROOM: ROOM_FRONT_YARD,
		},
		"pan_2": {
			DATA_ROOM: ROOM_BACKYARD,
		},
	}

	cameras = {
		camera_slug: {
			**basic_cameras[camera_slug],
			**customizations.get(camera_slug, {})
		} for camera_slug in basic_cameras
	}

	for camera_data in cameras.values():
		camera_data.setdefault(DATA_NICKNAME, camera_data[DATA_ROOM])
		camera_data.setdefault(DATA_FULL_NAME, f"{camera_data[DATA_NICKNAME]} Camera")
		camera_data.setdefault(DATA_IN_VIEW, {})
		camera_data[DATA_IN_VIEW].setdefault(DATA_GARAGE_DOORS, set())
		camera_data[DATA_IN_VIEW].setdefault(DATA_LIGHTS, set())
		camera_data[DATA_IN_VIEW].setdefault(DATA_LOCKS, set())
		camera_data.setdefault(DATA_VIDEO_QUALITY, 5)
		camera_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

	# TODO: wait until I've cleaned up the All Entities dashboard of unrelated and other loose things such that I rarely need to open it (and load all the cameras, crashing the network)
	return cameras
	# return {}


async def generate_yaml(**kwds):
	cameras = await get_cameras(**kwds)

	ffmpeg_cameras = [
		{
			CONF_EXTRA_ARGUMENTS: f'-q:v {camera_data[DATA_VIDEO_QUALITY]}',
			CONF_INPUT: f'-rtsp_transport udp -analyzeduration 1000000 -probesize 1000000 -i {camera_data[DATA_STREAM_SOURCE]}',
			CONF_NAME: camera_slug,
			CONF_PLATFORM: PLATFORM_FFMPEG,
		} for camera_slug, camera_data in cameras.items()
	]

	return {
		DOMAIN_CAMERA: ffmpeg_cameras,
	}


async def customize(**kwds):
	cameras = await get_cameras(**kwds)

	customize_ffmpeg_cameras = {
		f"{DOMAIN_CAMERA}.{camera_slug}": {
			ATTR_FRIENDLY_NAME: camera_data[DATA_FULL_NAME],
			ATTR_ICON: ICON_MDI_CCTV,
		} for camera_slug, camera_data in cameras.items()
	}

	return {
		**customize_ffmpeg_cameras,
	}
