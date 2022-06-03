"Registered all the cameras with the home automation and security system"

from parse import compile as parse_compile

from custom_components.custom_backend.const import (
	ATTR_ENTITY_PICTURE,
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	CONF_EXTRA_ARGUMENTS,
	CONF_INPUT,
	CONF_NAME,
	CONF_PLATFORM,
	DATA_CAMERA,
	DATA_FULL_NAME,
	DATA_GARAGE_DOORS,
	DATA_ICON,
	DATA_IN_VIEW,
	DATA_LIGHTS,
	DATA_LOCKS,
	DATA_NICKNAME,
	DATA_ROOM,
	DATA_SECRETS,
	DATA_STREAM_SOURCE,
	DATA_UNIFI_DEVICE_TRACKER_SLUG,
	DATA_VIDEO_QUALITY,
	DATA_WYZE,
	DATA_ZONE,
	DOMAIN_CAMERA,
	DOMAIN_DEVICE_TRACKER,
	GARAGE_DOOR_GARAGE_DOOR,
	ICON_MDI_CCTV,
	IMAGE_WYZE_LOGO,
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


async def get_cameras(**kwds):
	secrets = kwds[DATA_SECRETS]

	def get_camera(slug):
		return {
			DATA_STREAM_SOURCE: secrets[f"{DATA_CAMERA}_{slug}_{DATA_STREAM_SOURCE}"],
		}

	camera_slugs = set()
	camera_slug_matcher = parse_compile(f"{DATA_CAMERA}_{{camera_slug}}_{DATA_STREAM_SOURCE}")
	for key in secrets:
		camera_slug_match = camera_slug_matcher.parse(key)
		if camera_slug_match is None:
			continue

		camera_slugs.add(camera_slug_match.named["camera_slug"])
	
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

	for camera_slug, camera_data in cameras.items():
		camera_data.setdefault(DATA_NICKNAME, camera_data[DATA_ROOM])
		camera_data.setdefault(DATA_FULL_NAME, f"{camera_data[DATA_NICKNAME]} Camera")
		camera_data.setdefault(DATA_ICON, ICON_MDI_CCTV)
		camera_data.setdefault(DATA_IN_VIEW, {})
		camera_data[DATA_IN_VIEW].setdefault(DATA_GARAGE_DOORS, set())
		camera_data[DATA_IN_VIEW].setdefault(DATA_LIGHTS, set())
		camera_data[DATA_IN_VIEW].setdefault(DATA_LOCKS, set())
		camera_data.setdefault(DATA_UNIFI_DEVICE_TRACKER_SLUG, f"{DATA_CAMERA}_{DATA_WYZE}_{camera_slug}")
		camera_data.setdefault(DATA_VIDEO_QUALITY, 5)
		camera_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

	return cameras


async def generate_yaml(**kwds):
	cameras = await get_cameras(**kwds)

	ffmpeg_cameras = [
		{
			# TODO: is this doing anything???
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
			ATTR_ICON: camera_data[DATA_ICON],
		} for camera_slug, camera_data in cameras.items()
	}

	customize_unifi_device_trackers = {
		f"{DOMAIN_DEVICE_TRACKER}.{camera_data[DATA_UNIFI_DEVICE_TRACKER_SLUG]}": {
			ATTR_ENTITY_PICTURE: IMAGE_WYZE_LOGO,
			ATTR_FRIENDLY_NAME: f"{camera_data[DATA_FULL_NAME]} Internet Connected",
			ATTR_ICON: camera_data[DATA_ICON],
		} for camera_data in cameras.values()
	}

	return {
		**customize_ffmpeg_cameras,
		**customize_unifi_device_trackers,
	}
