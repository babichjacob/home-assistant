"Generated ui-lovelace.yaml"

from custom_components.custom_backend.config.packages.frontend import get_devices_by_type_dashboard

async def generate_yaml(**kwds):
	main_dashboard = await get_devices_by_type_dashboard(**kwds)

	return main_dashboard
