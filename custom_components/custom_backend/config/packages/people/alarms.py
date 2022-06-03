"Keeping track of each person's alarm"

from datetime import datetime, timedelta
from logging import getLogger

from homeassistant import core
from homeassistant.helpers.event import async_track_point_in_time

from custom_components.custom_backend.const import (
	CONF_DATETIME,
	CONF_ENTITY_ID,
	CONF_HAS_DATE,
	CONF_HAS_TIME,
	CONF_ICON,
	CONF_MAX,
	CONF_MIN,
	CONF_MODE,
	CONF_NAME,
	CONF_STEP,
	CONF_UNIT_OF_MEASUREMENT,
	CONF_VALUE,
	DATA_ALARM,
	DATA_AUDIO,
	DATA_BEDTIME_SHIFT,
	DATA_FIRST_ALARM_TODAY,
	DATA_FULL_NAME,
	DATA_GROUP,
	DATA_IMAGE,
	DATA_LAST_ALARM,
	DATA_LEISURE,
	DATA_MESSAGE,
	DATA_MESSAGE_HTML,
	DATA_NEXT_ALARM,
	DATA_NICKNAME,
	DATA_PEOPLE,
	DATA_PRIORITY,
	DATA_PUSH,
	DATA_TEXT,
	DATA_TITLE,
	DATA_TTS,
	DOMAIN_INPUT_DATETIME,
	DOMAIN_INPUT_NUMBER,
	EVENT_TYPE_HOMEASSISTANT_START,
	ICON_MDI_ALARM,
	ICON_MDI_BED,
	IMAGE_ALARM_CLOCK_COLOR,
	IMAGE_EXPIRED_COLOR,
	IMAGE_FUTURE_COLOR,
	PRIORITY_LOW,
	PRIORITY_URGENT,
	PUSH_SOUND_ALARM_NIGHTSTAND_HAPTIC,
	SERVICE_SET_VALUE,
	TIME_FORMAT_INPUT_DATETIME,
	SERVICE_SET_DATETIME,
	TIME_FORMAT_PRETTY_DATE,
	TIME_FORMAT_PRETTY_TIME,
	TIME_FORMAT_PRETTY_TIME_ON_DATE,
	UNIT_OF_MEASUREMENT_MINUTE,
)
from custom_components.custom_backend.utils import entity_state_to_readable_store, window

from custom_components.custom_backend.config.packages.notify import notify


GROUP_SLEEP_CYCLE = "Sleep Cycle"

_LOGGER = getLogger(__name__)


def filter_to_people_with_alarms(people):
	return {person_slug: person_data for person_slug, person_data in people.items() if person_data[DATA_ALARM]}


async def generate_yaml(**kwds):
	people = kwds[DATA_PEOPLE]

	people_with_alarms = filter_to_people_with_alarms(people)

	create_people_first_alarm_today_input_datetimes = {
		f"{person_slug}_{DATA_FIRST_ALARM_TODAY}": {
			CONF_HAS_DATE: True,
			CONF_HAS_TIME: True,
			CONF_ICON: ICON_MDI_ALARM,
			CONF_NAME: f"{person_data[DATA_FULL_NAME]}'s First Alarm Today",
		} for person_slug, person_data in people_with_alarms.items()
	}

	create_people_most_recent_alarm_input_datetimes = {
		f"{person_slug}_{DATA_LAST_ALARM}": {
			CONF_HAS_DATE: True,
			CONF_HAS_TIME: True,
			CONF_ICON: ICON_MDI_ALARM,
			CONF_NAME: f"{person_data[DATA_FULL_NAME]}'s Most Recent Alarm",
		} for person_slug, person_data in people_with_alarms.items()
	}

	create_people_next_alarm_input_datetimes = {
		f"{person_slug}_{DATA_NEXT_ALARM}": {
			CONF_HAS_DATE: True,
			CONF_HAS_TIME: True,
			CONF_ICON: ICON_MDI_ALARM,
			CONF_NAME: f"{person_data[DATA_FULL_NAME]}'s Next Alarm",
		} for person_slug, person_data in people_with_alarms.items()
	}

	create_people_bedtime_shift_input_numbers = {
		f"{person_slug}_{DATA_BEDTIME_SHIFT}": {
			CONF_ICON: ICON_MDI_BED,
			CONF_MAX: 180,
			CONF_MIN: -180,
			CONF_MODE: "slider",
			CONF_NAME: f"{person_data[DATA_FULL_NAME]}'s Bedtime Shift",
			CONF_STEP: 10,
			CONF_UNIT_OF_MEASUREMENT: UNIT_OF_MEASUREMENT_MINUTE,
		} for person_slug, person_data in people_with_alarms.items()
	}

	return {
		DOMAIN_INPUT_DATETIME: {
			**create_people_first_alarm_today_input_datetimes,
			**create_people_most_recent_alarm_input_datetimes,
			**create_people_next_alarm_input_datetimes,
		},
		DOMAIN_INPUT_NUMBER: {
			**create_people_bedtime_shift_input_numbers,
		}
	}



async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	people = kwds[DATA_PEOPLE]

	people_with_alarms = filter_to_people_with_alarms(people)

	actual_alarm_time_for_person = {}
	async def alarm_going_off(*, point_in_time, person_slug):
		point_in_time = point_in_time.replace(tzinfo=None)
		expected_alarm_time = actual_alarm_time_for_person.get(person_slug)
		if expected_alarm_time is not None:
			if point_in_time != expected_alarm_time:
				_LOGGER.warning(f"{person_slug}'s alarm is an old value: {point_in_time} vs expected {expected_alarm_time}")
				return

		now = datetime.now().replace(tzinfo=None)

		time_since_alarm = now - point_in_time
		_LOGGER.warning(f"time_since_alarm: {time_since_alarm}")
		missed = True
		if time_since_alarm < timedelta(seconds=5):
			missed = False

		person_data = people[person_slug]
		# TODO: check for activities tomorrow
		next_alarm_time = person_data[DATA_ALARM][DATA_LEISURE]
		today = now.date()
		tomorrow = today + timedelta(days=1)
		next_alarm_datetime = datetime.combine(tomorrow, next_alarm_time)

		next_alarm_entity_id = f"{DOMAIN_INPUT_DATETIME}.{person_slug}_{DATA_NEXT_ALARM}"

		await hass.services.async_call(DOMAIN_INPUT_DATETIME, SERVICE_SET_DATETIME, {
			CONF_ENTITY_ID: next_alarm_entity_id,
			CONF_DATETIME: next_alarm_datetime.strftime(TIME_FORMAT_INPUT_DATETIME),
		}, blocking=True)

		last_alarm_entity_id = f"{DOMAIN_INPUT_DATETIME}.{person_slug}_{DATA_LAST_ALARM}"
		last_alarm = hass.states.get(last_alarm_entity_id).state
		last_alarm_datetime = datetime.strptime(last_alarm, TIME_FORMAT_INPUT_DATETIME)

		if last_alarm_datetime < point_in_time:
			await hass.services.async_call(DOMAIN_INPUT_DATETIME, SERVICE_SET_DATETIME, {
				CONF_ENTITY_ID: last_alarm_entity_id,
				CONF_DATETIME: point_in_time.strftime(TIME_FORMAT_INPUT_DATETIME),
			}, blocking=True)
		else:
			_LOGGER.error("??? last_alarm is further in the future than this alarm")

		first_alarm_today_entity_id = f"{DOMAIN_INPUT_DATETIME}.{person_slug}_{DATA_FIRST_ALARM_TODAY}"
		first_alarm_today = hass.states.get(first_alarm_today_entity_id).state
		first_alarm_today_datetime = datetime.strptime(first_alarm_today, TIME_FORMAT_INPUT_DATETIME)

		this_is_the_first_alarm_today = first_alarm_today_datetime.date() != today

		if this_is_the_first_alarm_today:
			_LOGGER.warning(f"setting {person_slug}'s first alarm today to {point_in_time}")
			await hass.services.async_call(DOMAIN_INPUT_DATETIME, SERVICE_SET_DATETIME, {
				CONF_ENTITY_ID: first_alarm_today_entity_id,
				CONF_DATETIME: point_in_time.strftime(TIME_FORMAT_INPUT_DATETIME),
			}, blocking=True)
		else:
			_LOGGER.warning(f"there was already an alarm earlier today for {person_slug} (at {first_alarm_today_datetime}) -- don't change it")
		
		if this_is_the_first_alarm_today or missed:
			await hass.services.async_call(DOMAIN_INPUT_NUMBER, SERVICE_SET_VALUE, {
				CONF_ENTITY_ID: f"{DOMAIN_INPUT_NUMBER}.{person_slug}_{DATA_BEDTIME_SHIFT}",
				CONF_VALUE: 0,
			}, blocking=True)

		
		notify_args = {}
		if missed:
			notify_args = {
				DATA_GROUP: GROUP_SLEEP_CYCLE,
				DATA_IMAGE: IMAGE_EXPIRED_COLOR,
				DATA_PEOPLE: [person_slug],
				DATA_PRIORITY: PRIORITY_URGENT,
				DATA_TEXT: {
					DATA_MESSAGE: f"{person_data[DATA_NICKNAME]}, your alarm was supposed to go off earlier but the home automation and security system missed it (it may have been offline)!",
					DATA_TITLE: "Alarm Happened Earlier",
				},
			}
		elif this_is_the_first_alarm_today:
			notify_args = {
				DATA_AUDIO: {
					DATA_PUSH: PUSH_SOUND_ALARM_NIGHTSTAND_HAPTIC,
				},
				DATA_GROUP: GROUP_SLEEP_CYCLE,
				DATA_IMAGE: IMAGE_ALARM_CLOCK_COLOR,
				DATA_PEOPLE: [person_slug],
				DATA_PRIORITY: PRIORITY_LOW,
				DATA_TEXT: {
					DATA_MESSAGE: f"Good morning {person_data[DATA_NICKNAME]}! Hope you have a good day ahead of you!",
					DATA_TITLE: "Good Morning",
				},
			}
		else:
			notify_args = {
				DATA_AUDIO: {
					DATA_PUSH: PUSH_SOUND_ALARM_NIGHTSTAND_HAPTIC,
				},
				DATA_GROUP: GROUP_SLEEP_CYCLE,
				DATA_IMAGE: IMAGE_ALARM_CLOCK_COLOR,
				DATA_PEOPLE: [person_slug],
				DATA_TEXT: {
					DATA_MESSAGE: f"{person_data[DATA_NICKNAME]}, your alarm is going off right now!",
					DATA_TITLE: "Alarm Going Off",
				},
			}
		
		if notify_args:
			await notify(notify_args, hass=hass, **kwds)
	

	def update_next_alarm_listener(*, next_alarm_datetime, person_slug):
		actual_alarm_time_for_person[person_slug] = next_alarm_datetime
		# TODO: replace with regular asyncio methods because home assistant's method is difficult to work with
		async_track_point_in_time(hass=hass, action=lambda point_in_time: hass.async_create_task(alarm_going_off(point_in_time=point_in_time, person_slug=person_slug)), point_in_time=next_alarm_datetime)


	async def next_alarm_is_newly_set(*, next_alarm_datetime, person_slug):
		update_next_alarm_listener(next_alarm_datetime=next_alarm_datetime, person_slug=person_slug)

		await notify({
			DATA_AUDIO: {
				DATA_TTS: f"Your alarm has been set for {next_alarm_datetime.strftime(TIME_FORMAT_PRETTY_TIME_ON_DATE)}",
			},
			DATA_GROUP: GROUP_SLEEP_CYCLE,
			DATA_IMAGE: IMAGE_FUTURE_COLOR,
			DATA_PEOPLE: [person_slug],
			DATA_PRIORITY: PRIORITY_LOW,
			DATA_TEXT: {
				DATA_MESSAGE: next_alarm_datetime.strftime(TIME_FORMAT_PRETTY_TIME_ON_DATE),
				DATA_MESSAGE_HTML: f"<b>{next_alarm_datetime.strftime(TIME_FORMAT_PRETTY_TIME)}</b> on <b>{next_alarm_datetime.strftime(TIME_FORMAT_PRETTY_DATE)}</b>",
				DATA_TITLE: "Alarm Set",
			},
		}, hass=hass, **kwds)


	async def setup_automations(event):
		for person_slug in people_with_alarms:
			next_alarm_entity_id = f"{DOMAIN_INPUT_DATETIME}.{person_slug}_{DATA_NEXT_ALARM}"

			next_alarm_store = entity_state_to_readable_store(next_alarm_entity_id, hass=hass)
			[get_next_alarm, _subscribe_to_next_alarm] = next_alarm_store

			next_alarm_datetime = datetime.strptime(get_next_alarm().state, TIME_FORMAT_INPUT_DATETIME)
			now = datetime.now()
			if next_alarm_datetime < now:
				_LOGGER.warning(f"startup: missed {person_slug}'s alarm!")
				await alarm_going_off(point_in_time=next_alarm_datetime, person_slug=person_slug)
			else:
				_LOGGER.warning(f"startup: {person_slug}'s alarm hasn't happened yet; will track it for {next_alarm_datetime}")
				update_next_alarm_listener(next_alarm_datetime=next_alarm_datetime, person_slug=person_slug)
			
			next_alarm_changes = window(next_alarm_store, 2)

			[_get_next_alarm_window, subscribe_to_next_alarm_changes] = next_alarm_changes
			subscribe_to_next_alarm_changes(lambda *, get_next_alarm=get_next_alarm, person_slug=person_slug: hass.async_create_task(next_alarm_is_newly_set(next_alarm_datetime=datetime.strptime(get_next_alarm().state, TIME_FORMAT_INPUT_DATETIME), person_slug=person_slug)))

	hass.bus.async_listen(EVENT_TYPE_HOMEASSISTANT_START, setup_automations)
	return True
