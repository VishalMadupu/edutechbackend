from .user_model import User, Project
from .edtech_models import Course, Video, Enrollment, Progress

# Aliases if used elsewhere, although User is the primary model now
Client = User
ServiceProvider = User
SuperAdmin = User
Student = User
Tutor = User
