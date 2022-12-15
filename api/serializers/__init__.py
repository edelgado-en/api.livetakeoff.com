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