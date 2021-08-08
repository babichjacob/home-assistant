"Registered everyone with the home automation and security system"

from datetime import time, timedelta

from custom_components.custom_backend.const import (
	COMPUTER_JACOB_S_DESKTOP,
	COMPUTER_JACOB_S_SCHOOL_LAPTOP,
	ATTR_ENTITY_PICTURE,
	CONF_ID,
	CONF_DEVICE_TRACKERS,
	CONF_NAME,
	CONF_USER_ID,
	DATA_ALARM,
	DATA_COMPUTERS,
	DATA_FULL_NAME,
	DATA_HOME,
	DATA_LEISURE,
	DATA_LOCK_SLOTS,
	DATA_NICKNAME,
	DATA_PERSON,
	DATA_PHONES,
	DATA_PHOTO,
	DATA_SHORT_NAME,
	DATA_SLEEP_DURATION,
	DATA_TABLETS,
	DATA_USER_ID,
	DATA_WIND_DOWN_BEFORE_FALLING_ASLEEP_DURATION,
	DOMAIN_PERSON,
	PERSON_BAKA,
	PERSON_GARY,
	PERSON_GLORIA,
	PERSON_HELGA,
	PERSON_JACKSON,
	PERSON_JACOB,
	PERSON_JENNA,
	PERSON_JILLIAN,
	PERSON_JORDAN,
	PERSON_JUSTIN,
	PERSON_MATT,
	PHONE_JACOB_S_HTC_U11,
	PHONE_JENNA_S_IPHONE_XR,
	PHONE_MATT_S_ONEPLUS_8,
	TABLET_MATT_S_2015_IPAD_PRO,
	ZONE_BAKA_S_HOUSE,
	ZONE_GARY_S_HOUSE,
	ZONE_GLORIA_S_HOUSE,
)


def get_people(**kwds):
	secrets = kwds["secrets"]

	def get_person(slug):
		return {
			DATA_FULL_NAME: secrets[f"{DATA_PERSON}_{slug}_{DATA_FULL_NAME}"],
			DATA_LOCK_SLOTS: secrets.get(f"{DATA_PERSON}_{slug}_{DATA_LOCK_SLOTS}", []),
			DATA_NICKNAME: secrets[f"{DATA_PERSON}_{slug}_{DATA_NICKNAME}"],
			DATA_PHOTO: f"/local/person/{slug}.png",
			DATA_USER_ID: secrets.get(f"{DATA_PERSON}_{slug}_{DATA_USER_ID}"),
		}

	person_slugs = set()

	for key in secrets:
		prefix = DATA_PERSON + "_"
		if not key.startswith(prefix):
			continue

		suffix = "_" + DATA_FULL_NAME
		if not key.endswith(suffix):
			continue

		person_slugs.add(key[len(prefix):-len(suffix)])
	
	people_without_customizations = {
		person_slug: get_person(person_slug) for person_slug in person_slugs
	}

	customizations = {
		PERSON_BAKA: {
			DATA_HOME: ZONE_BAKA_S_HOUSE,
		},
		PERSON_GARY: {
			DATA_HOME: ZONE_GARY_S_HOUSE,
		},
		PERSON_HELGA: {
			DATA_HOME: ZONE_GARY_S_HOUSE,
		},
		PERSON_GLORIA: {
			DATA_HOME: ZONE_GLORIA_S_HOUSE,
		},
		PERSON_JACKSON: {
			DATA_HOME: ZONE_GARY_S_HOUSE,
		},
		PERSON_JACOB: {
			DATA_ALARM: {
				DATA_LEISURE: time(hour=11, minute=40),
				DATA_SLEEP_DURATION: timedelta(hours=8),
				DATA_WIND_DOWN_BEFORE_FALLING_ASLEEP_DURATION: timedelta(hours=1, minutes=30),
			},
			DATA_COMPUTERS: {COMPUTER_JACOB_S_DESKTOP, COMPUTER_JACOB_S_SCHOOL_LAPTOP},
			DATA_HOME: ZONE_BAKA_S_HOUSE,
			DATA_PHONES: {PHONE_JACOB_S_HTC_U11},
		},
		PERSON_JENNA: {
			DATA_HOME: ZONE_BAKA_S_HOUSE,
			DATA_PHONES: {PHONE_JENNA_S_IPHONE_XR},
		},
		PERSON_JILLIAN: {
			DATA_HOME: ZONE_GARY_S_HOUSE,
		},
		PERSON_JORDAN: {
			DATA_HOME: ZONE_GLORIA_S_HOUSE,
		},
		PERSON_JUSTIN: {
			DATA_HOME: ZONE_GLORIA_S_HOUSE,
		},
		PERSON_MATT: {
			DATA_HOME: ZONE_BAKA_S_HOUSE,
			DATA_PHONES: {PHONE_MATT_S_ONEPLUS_8},
			DATA_TABLETS: {TABLET_MATT_S_2015_IPAD_PRO},
		},
	}

	people = {
		person_slug: {
			**people_without_customizations[person_slug],
			**customizations.get(person_slug, {})
		} for person_slug in people_without_customizations
	}

	for person_data in people.values():
		person_data.setdefault(DATA_ALARM, {})
		person_data.setdefault(DATA_COMPUTERS, [])
		person_data.setdefault(DATA_HOME, None)
		person_data.setdefault(DATA_PHONES, [])
		person_data.setdefault(DATA_TABLETS, [])

	return people


async def generate_yaml(**kwds):
	people = kwds["people"]

	return {
		DOMAIN_PERSON: [
			{
				CONF_NAME: person_data[DATA_FULL_NAME],
				CONF_ID: person_slug,
				**({CONF_USER_ID: person_data[DATA_USER_ID]} if person_data[DATA_USER_ID] is not None else {}),
				CONF_DEVICE_TRACKERS: [], # TODO
			} for person_slug, person_data in people.items()
		],
	}


def exposed_devices(**kwds):
	people = kwds["people"]

	return {
		f"{DOMAIN_PERSON}.{person_slug}": {
			DATA_SHORT_NAME: person_data[DATA_NICKNAME],
			DATA_FULL_NAME: person_data[DATA_FULL_NAME],
		} for person_slug, person_data in people.items()
	}


async def customize(**kwds):
	people = kwds["people"]

	return {
		f"{DOMAIN_PERSON}.{person_slug}": {
			ATTR_ENTITY_PICTURE: person_data[DATA_PHOTO],
		} for person_slug, person_data in people.items()
	}
