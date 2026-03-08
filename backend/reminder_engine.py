def get_next_reminder(medications):
    for m in medications:
        if not m.get('taken'):
            return m
    return None
