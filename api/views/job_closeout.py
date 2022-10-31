import pdb
from django.http import FileResponse, HttpResponse
from rest_framework .response import Response
from rest_framework import (permissions, status)
import io
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm, cm
from reportlab.pdfbase.ttfonts import TTFont

from rest_framework.views import APIView


import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from api.models import (Job, JobPhotos)

class JobCloseoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        if not self.can_closeout_job(request.user):
            return Response({'error': 'You do not have permission to view close out job'}, status=status.HTTP_403_FORBIDDEN)

        job = Job.objects.select_related('airport').select_related('fbo').get(pk=id)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "TC.pdf"'

        doc = SimpleDocTemplate(response, rightMargin=42,
                            leftMargin=42, topMargin=42, bottomMargin=18)

        Story=[]

        # Add a background color as a letter head
        
        
        im = Image('https://res.cloudinary.com/datidxeqm/image/upload/v1667093825/media/profiles/N334JE_BCT_2022-10-28_0_suotul.png', 1*inch, 1*inch)
        im.hAlign = 'RIGHT'
        #im._restrictSize(1.5 * inch, 1.5 * inch)
        Story.append(im)
        Story.append(Spacer(1, 12))

        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        
        
        Story.append(Paragraph('Job Close Out', styles["Heading1"]))

        details = [
                ['', ''],
                ['Purchase Order', job.purchase_order],
                ['Tail Number', job.tailNumber],
                ['Airport', job.airport.name],
                ['FBO', job.fbo.name],
                ['Completetion Date', 'Need to get this value from the activity table: job completed'],
            ]

        t = Table(details, hAlign='LEFT')
        t.setStyle(TableStyle(
                        [
                            ('LEFTPADDING', (0, 0), (-1, -1), 7),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                            ('TOPPADDING', (0, 0), (-1, -1), 7),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('FONTNAME', (0,0), (0,-1), 'Times-Bold')
                        ]
                    )
                 )

        #t.setStyle(TableStyle([('BACKGROUND')]))

        Story.append(t)

        Story.append(Spacer(1, 24))


        # Create return address
        """ ptext = '%s' % full_name
        
        Story.append(Paragraph(ptext, styles["Normal"]))       
        for part in address_parts:
            ptext = '%s' % part.strip()
            Story.append(Paragraph(ptext, styles["Normal"]))   
        
        Story.append(Spacer(1, 12))
        ptext = 'Dear %s:' % full_name.split()[0].strip()
        
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        
        ptext = 'We would like to welcome you to our subscriber base for %s Magazine! \
                You will receive %s issues at the excellent introductory price of $%s. Please respond by\
                %s to start receiving your subscription and get the following free gift: %s.' % (magName, 
                                                                                                        issueNum,
                                                                                                        subPrice,
                                                                                                        limitedDate,
                                                                                                        freeGift)
        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 12)) """

        """ Story.append(Spacer(1, 24))
        Story.append(Paragraph('Thank you for you order.', styles["Justify"]))
        Story.append(Spacer(1, 12)) """

        
        Story.append(Paragraph('Interior Photos', styles["Heading2"]))
        Story.append(Spacer(1, 24))

        interior_photos = JobPhotos.objects.filter(job_id=id, interior=True).all()
        for photo in interior_photos:
            im = Image(photo.image.url, 4*inch, 4*inch)
            Story.append(im)
            Story.append(Spacer(1, 36))


        Story.append(Paragraph('Exterior Photos', styles["Heading2"]))
        Story.append(Spacer(1, 24))

        exterior_photos = JobPhotos.objects.filter(job_id=id, interior=False).all()
        for photo in exterior_photos:
            im = Image(photo.image.url, 4*inch, 4*inch)
            Story.append(im)
            Story.append(Spacer(1, 36)) 

        doc.build(Story)

        return response

        
    def can_closeout_job(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True
        
        return False

