import pdb
from django.http import FileResponse, HttpResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib import utils
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
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

    def get_image(self, path, width=1*cm):
        img = utils.ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        return Image(path, width=width, height=(width * aspect))

    def get(self, request, id):
        job = Job.objects.select_related('airport').select_related('fbo').get(pk=id)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "TC.pdf"'

        doc = SimpleDocTemplate(response, rightMargin=42,
                            leftMargin=42, topMargin=42, bottomMargin=18)

        Story=[]
        # variables
        magName = "Pythonista"
        issueNum = 12
        subPrice = "99.00"
        limitedDate = "03/05/2010"
        freeGift = "tin foil hat"
        formatted_time = time.ctime()
        full_name = "Mike Driscoll"
        address_parts = ["411 State St.", "Marshalltown, IA 50158"]
        
        im = Image('https://res.cloudinary.com/datidxeqm/image/upload/v1667093825/media/profiles/N334JE_BCT_2022-10-28_0_suotul.png', 2*inch, 2*inch)
        #im._restrictSize(1.5 * inch, 1.5 * inch)
        Story.append(im)
        Story.append(Spacer(1, 12))

        styles=getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        
        ptext = '%s' % formatted_time
        
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

        #t.setStyle(TableStyle([('BACKGROUND')]))

        Story.append(t)


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

        Story.append(Spacer(1, 24))
        Story.append(Paragraph('Thank you for you order.', styles["Justify"]))
        Story.append(Spacer(1, 12))

        
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

        


