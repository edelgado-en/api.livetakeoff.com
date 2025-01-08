from .job import JobSerializer
from .job_detail import JobDetailSerializer
from .job_service_assignment import (
    GenericServiceAssignmentSerializer,
    JobServiceAssignmentSerializer,
    JobRetainerServiceAssignmentSerializer)

from .job_photo import JobPhotoSerializer
from .basic_user import BasicUserSerializer
from .job_comment import JobCommentSerializer
from .job_admin import JobAdminSerializer
from .edit_job import JobEditSerializer
from .service import ServiceSerializer
from .job_detail_basic import JobDetailBasicSerializer
from .customer import CustomerSerializer
from .price_list import PriceListSerializer
from .customer_settings import CustomerSettingsSerializer
from .customer_detail import CustomerDetailSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .retainer_service import RetainerServiceSerializer
from .vendor import VendorSerializer
from .job_completed import JobCompletedSerializer
from .job_activity import JobActivitySerializer
from .aircraft_type import AircraftTypeSerializer
from .shared_job_detail import SharedJobDetailSerializer
from .customer_activity import CustomerActivitySerializer
from .job_estimate_detail import JobEstimateDetailSerializer
from .job_estimate_basic import JobEstimateSerializer
from .job_basic import JobBasicSerializer
from .tail_stats import TailStatsSerializer
from .customer_retainer import CustomerRetainerSerializer
from .users import UsersSerializer
from .job_tag import JobTagSerializer
from .tail_alert import TailAlertSerializer
from .tag import TagSerializer
from .service_activity import ServiceActivitySerializer
from .retainer_service_activity import RetainerServiceActivitySerializer
from .job_file import JobFileSerializer
from .tail_file import TailFileSerializer
from .job_schedule import JobScheduleSerializer
from .user_profile import UserProfileSerializer
from .help_file import HelpFileSerializer
from .job_master_pm import JobMasterPmSerializer
from .vendor_detail import VendorDetailSerializer
from .vendor_file import VendorFileSerializer
from .customer_follower_email import CustomerFollowerEmailSerializer