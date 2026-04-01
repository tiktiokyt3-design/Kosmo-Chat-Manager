import time
import os
from database.storage_role import get_role


roles_number = {
    "user": 0,
    "moderator": 1,
    "admin": 2,
    "st.admin": 3,
    "owner": 4,
    "manager": 5,
    "dayn": 6,
    "owner_bot": 7
}

roles_name = {
    "user": "👤 Пользователь",
    "moderator": "👮 Модератор",
    "admin": "💫 Администратор",
    "st.admin": "💼 Старший Администратор",
    "owner": "👑 Владелец",
    "manager": "👩‍💼 Менеджер",
    "dayn": "👍 Красивая девушка",
    "owner_bot": "‼️ Владелец бота"
}
