from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DeveloperProfile
from .forms import DeveloperProfileForm
import qrcode
import io
import base64
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from PIL import Image
import os

@login_required
def dashboard(request):
    profile, created = DeveloperProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = DeveloperProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            return redirect('badges:dashboard')
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil.")
    else:
        form = DeveloperProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form
    }
    return render(request, 'badges/dashboard.html', context)

@login_required
def generate_badge(request):
    profile = request.user.developerprofile
    qr_code = None
    
    if profile.linkedin_url:
        qr_code = generate_qr_code(profile.linkedin_url)
    
    context = {
        'profile': profile,
        'qr_code': qr_code
    }
    return render(request, 'badges/badge_generator.html', context)

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

@login_required
def generate_dev_card(request):
    # Créer un buffer pour le PDF
    buffer = io.BytesIO()
    
    # Créer le PDF avec ReportLab
    p = canvas.Canvas(buffer, pagesize=(85*mm, 54*mm))  # Format carte de crédit
    
    # Fond avec dégradé
    p.setFillColorRGB(0.1, 0.11, 0.17)  # Couleur sombre
    p.rect(0, 0, 85*mm, 54*mm, fill=1)
    
    profile = request.user.developerprofile
    
    # Photo de profil
    if profile.profile_picture:
        try:
            img = Image.open(profile.profile_picture.path)
            img = img.resize((60, 60))  # Redimensionner
            p.drawInlineImage(img, 15, 54*mm-75, 60, 60)
        except:
            pass  # Gérer l'absence d'image
    
    # Informations textuelles
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(80, 54*mm-30, profile.user.get_full_name() or profile.user.username)
    
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.cyan)
    p.drawString(80, 54*mm-45, profile.job_title or "")
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica", 8)
    p.drawString(80, 54*mm-60, profile.location or "")
    
    # QR Code
    if profile.linkedin_url:
        qr = qrcode.QRCode(version=1, box_size=2, border=1)
        qr.add_data(profile.linkedin_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="white", back_color=None)
        
        # Convertir l'image QR en bytes
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_bytes = qr_buffer.getvalue()
        
        # Dessiner le QR code
        p.drawInlineImage(Image.open(io.BytesIO(qr_bytes)), 85*mm-60, 54*mm-60, 50, 50)
    
    # Technologies
    x_offset = 15
    y_offset = 15
    for tech in profile.tech_stack.all()[:6]:  # Limiter à 6 technologies
        if tech.icon:
            try:
                icon = Image.open(tech.icon.path)
                icon = icon.resize((20, 20))
                icon_buffer = io.BytesIO()
                icon.save(icon_buffer, format='PNG')
                icon_bytes = icon_buffer.getvalue()
                p.drawInlineImage(Image.open(io.BytesIO(icon_bytes)), x_offset, y_offset, 20, 20)
                x_offset += 25
                if x_offset > 60*mm:  # Nouvelle ligne
                    x_offset = 15
                    y_offset += 25
            except Exception as e:
                print(f"Erreur avec l'icône: {e}")
                continue
    
    # Finaliser le PDF
    p.showPage()
    p.save()
    
    # Renvoyer le PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dev_card.pdf"'
    
    return response
