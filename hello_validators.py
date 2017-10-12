def validate_World(message):
	if not message.text:
		return False

	return True

def validate_Hello(message):
	if not message.world:
		return False

	if not validate_World(message.world):
		return False

	return True

