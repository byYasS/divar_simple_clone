import logging


logger = logging.getLogger(__name__)


def send_sms(phone, otp):
    logger.info("Simulation SMS | Phone Number : %s", phone)
    logger.info("Your 6-digit code is : %s", otp)
    