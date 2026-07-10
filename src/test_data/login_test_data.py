from src.models.types import LoginDetails

LOGIN_USERS = {
    "admin": LoginDetails("admin@practicesoftwaretesting.com", "welcome01"),
    "approved": LoginDetails("customer2@practicesoftwaretesting.com", "welcome01"),
    "unapproved": LoginDetails("wrongMail", "00"),
}

