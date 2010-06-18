#coding: utf-8

from clinicaltrials.repository.trds_forms import MultilingualBaseFormSet
from django.template.context import RequestContext
from reviewapp.models import Attachment, Submission, SUBMISSION_STATUS
from reviewapp.forms import ExistingAttachmentForm,NewAttachmentForm

from repository.models import ClinicalTrial, Descriptor, TrialNumber
from repository.models import TrialSecondarySponsor, TrialSupportSource, Outcome
from repository.models import PublicContact, ScientificContact, SiteContact, Contact

from repository.trds_forms import GeneralHealthDescriptorForm, PrimarySponsorForm
from repository.trds_forms import SecondaryIdForm, SecondarySponsorForm
from repository.trds_forms import SupportSourceForm, TrialIdentificationForm
from repository.trds_forms import SpecificHealthDescriptorForm, HealthConditionsForm
from repository.trds_forms import InterventionDescriptorForm, InterventionForm
from repository.trds_forms import RecruitmentForm, StudyTypeForm, PrimaryOutcomesForm
from repository.trds_forms import SecondaryOutcomesForm, PublicContactForm
from repository.trds_forms import ScientificContactForm, ContactForm, NewInstitution
from repository.trds_forms import SiteContactForm

import choices
import settings
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory, modelformset_factory
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.db.models import Q
from django.views.generic.list_detail import object_list
from django.conf import settings

EXTRA_FORMS = 1
TRIAL_FORMS = ['Trial Identification',
               'Sponsors',
               'Health Conditions',
               'Interventions',
               'Recruitment',
               'Study Type',
               'Outcomes',
               'Contacts',
               'Attachments']


@login_required
def edit_trial_index(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    if request.POST:
        sub = ct.submission
        sub.status = SUBMISSION_STATUS[1][0]

        sub.save()
        return HttpResponseRedirect(reverse('reviewapp.dashboard'))
    else:
        ''' start view '''

        links = []
        for i, name in enumerate(TRIAL_FORMS):
            data = dict(label=_(name))
            data['url'] = reverse('step_' + str(i + 1), args=[trial_pk])
            data['icon'] = settings.MEDIA_URL + 'media/img/admin/icon_alert.gif'
            data['msg'] = _('Blank fields')
            links.append(data)
        return render_to_response('repository/trial_index.html',
                                  {'trial_pk':trial_pk,
                                   'submission':ct.submission,
                                   'links':links},
                                   context_instance=RequestContext(request))

def full_view(request, trial_pk):
    ''' full view '''
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))
    return render_to_response('repository/trds.html',
                              {'fieldtable':ct.html_dump()},
                               context_instance=RequestContext(request))


def index(request):
    latest_clinicalTrials = ClinicalTrial.objects.all()[:5]
    t = loader.get_template('repository/latest_clinicalTrials.html')
    c  = RequestContext(request,{
        'latest_clinicalTrials': latest_clinicalTrials,
    })
    return HttpResponse(t.render(c))

def details(request, trial_pk):
    ''' clinical trial details '''
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))
    translations = [t for t in ct.translations.all()]
    return render_to_response('repository/clinicaltrial_detail.html',
                                {'object': ct,
                                'translations': translations,
                                'host': request.get_host()},
                                context_instance=RequestContext(request))

@login_required
def new_institution(request):

    if request.POST:
        new_institution = NewInstitution(request.POST)
        if new_institution.is_valid():
            institution = new_institution.save()
            json = serializers.serialize('json',[institution])
            return HttpResponse(json, mimetype='application/json');
    else:
        new_institution = NewInstitution()

    return render_to_response('repository/new_institution.html',
                             {'form':new_institution},
                               context_instance=RequestContext(request))

def step_list(trial_pk):
    import sys
    current_step = int( sys._getframe(1).f_code.co_name.replace('step_','') )
    steps = []
    for i in range(1,10):
        steps.append((reverse('step_%d'%i,args=[trial_pk]), i == current_step))
    return steps

@login_required
def step_1(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    if request.POST:
        form = TrialIdentificationForm(request.POST, instance=ct)
        SecondaryIdSet = inlineformset_factory(ClinicalTrial, TrialNumber,
                                               form=SecondaryIdForm,
                                               extra=EXTRA_FORMS)
        secondary_forms = SecondaryIdSet(request.POST, instance=ct)

        if form.is_valid() and secondary_forms.is_valid():
            form.save()
            secondary_forms.save()
            return HttpResponseRedirect(reverse('step_1',args=[trial_pk]))
    else:
        form = TrialIdentificationForm(instance=ct)
        SecondaryIdSet = inlineformset_factory(ClinicalTrial, TrialNumber,
                                               form=SecondaryIdForm,
                                               extra=EXTRA_FORMS, can_delete=True)
        secondary_forms = SecondaryIdSet(instance=ct)

    forms = [form]
    formsets = [secondary_forms]
    return render_to_response('repository/trial_form.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[0],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Sponsors and Sources of Support'),
                               # As duas variaveis de contexto abaixo devem ir sempre que houver um form com translation
                               'available_languages': form.available_languages,
                               'default_second_language': form.default_second_language,
                               },
                               context_instance=RequestContext(request))


@login_required
def step_2(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    if request.POST:
        form = PrimarySponsorForm(request.POST, instance=ct)
        SecondarySponsorSet = inlineformset_factory(ClinicalTrial, TrialSecondarySponsor,
                           form=SecondarySponsorForm,extra=EXTRA_FORMS)
        SupportSourceSet = inlineformset_factory(ClinicalTrial, TrialSupportSource,
                           form=SupportSourceForm,extra=EXTRA_FORMS)

        secondary_forms = SecondarySponsorSet(request.POST, instance=ct)
        sources_form = SupportSourceSet(request.POST, instance=ct)

        if form.is_valid() and secondary_forms.is_valid() and sources_form.is_valid():
            form.save()
            secondary_forms.save()
            sources_form.save()
        return HttpResponseRedirect(reverse('step_2',args=[trial_pk]))
    else:
        form = PrimarySponsorForm(instance=ct)
        SecondarySponsorSet = inlineformset_factory(ClinicalTrial, TrialSecondarySponsor,
            form=SecondarySponsorForm,extra=EXTRA_FORMS, can_delete=True)
        SupportSourceSet = inlineformset_factory(ClinicalTrial, TrialSupportSource,
               form=SupportSourceForm,extra=EXTRA_FORMS,can_delete=True)

        secondary_forms = SecondarySponsorSet(instance=ct)
        sources_form = SupportSourceSet(instance=ct)

    forms = [form]
    formsets = [secondary_forms,sources_form]
    return render_to_response('repository/step_2.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[1],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Health Conditions Form')},
                               context_instance=RequestContext(request))


@login_required
def step_3(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    GeneralDescriptorSet = modelformset_factory(Descriptor,
                                                form=GeneralHealthDescriptorForm,
                                                can_delete=True,
                                                extra=EXTRA_FORMS)

    SpecificDescriptorSet = modelformset_factory(Descriptor,
                                                form=SpecificHealthDescriptorForm,
                                                can_delete=True,
                                                extra=EXTRA_FORMS)

    general_qs = Descriptor.objects.filter(trial=trial_pk,
                                           aspect=choices.TRIAL_ASPECT[0][0],
                                           level=choices.DESCRIPTOR_LEVEL[0][0])

    specific_qs = Descriptor.objects.filter(trial=trial_pk,
                                           aspect=choices.TRIAL_ASPECT[0][0],
                                           level=choices.DESCRIPTOR_LEVEL[1][0])

    if request.POST:
        form = HealthConditionsForm(request.POST, instance=ct)
        general_desc_formset = GeneralDescriptorSet(request.POST,queryset=general_qs,prefix='g')
        specific_desc_formset = SpecificDescriptorSet(request.POST,queryset=specific_qs,prefix='s')

        if form.is_valid() and general_desc_formset.is_valid() and specific_desc_formset.is_valid():
            descriptors = general_desc_formset.save(commit=False)
            descriptors += specific_desc_formset.save(commit=False)
            

            for descriptor in descriptors:
                descriptor.trial = ct

            form.save()
            general_desc_formset.save()
            specific_desc_formset.save()
            
            return HttpResponseRedirect(reverse('step_3',args=[trial_pk]))
    else:
        form = HealthConditionsForm(instance=ct)
        general_desc_formset = GeneralDescriptorSet(queryset=general_qs,prefix='g')
        specific_desc_formset = SpecificDescriptorSet(queryset=specific_qs,prefix='s')


    forms = [form]
    formsets = [general_desc_formset, specific_desc_formset]
    return render_to_response('repository/step_3.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[2],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Interventions Form')},
                               context_instance=RequestContext(request))


@login_required
def step_4(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    DescriptorFormSet = modelformset_factory(Descriptor,
                                          form=InterventionDescriptorForm,
                                          extra=EXTRA_FORMS)

    queryset = Descriptor.objects.filter(trial=trial_pk,
                                           aspect=choices.TRIAL_ASPECT[1][0],
                                           level=choices.DESCRIPTOR_LEVEL[0][0])
    if request.POST:
        form = InterventionForm(request.POST, instance=ct)
        specific_desc_formset = DescriptorFormSet(request.POST, queryset=queryset)

        if form.is_valid() and specific_desc_formset.is_valid():
            descriptors = specific_desc_formset.save(commit=False)


            for descriptor in descriptors:
                descriptor.trial = ct

            specific_desc_formset.save()
            form.save()
            return HttpResponseRedirect(reverse('step_4',args=[trial_pk]))
    else:
        form = InterventionForm(instance=ct)
        specific_desc_formset = DescriptorFormSet(queryset=queryset)

    forms = [form]
    formsets = [specific_desc_formset]
    return render_to_response('repository/step_4.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[3],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Recruitment Form')},
                               context_instance=RequestContext(request))


@login_required
def step_5(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    if request.POST:
        form = RecruitmentForm(request.POST, instance=ct)

        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('step_5',args=[trial_pk]))
    else:
        form = RecruitmentForm(instance=ct)

    forms = [form]
    return render_to_response('repository/trial_form.html',
                              {'forms':forms,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[4],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Study Type Form')},
                               context_instance=RequestContext(request))


@login_required
def step_6(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    if request.POST:
        form = StudyTypeForm(request.POST, instance=ct)

        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('step_6',args=[trial_pk]))
    else:
        form = StudyTypeForm(instance=ct)

    forms = [form]
    return render_to_response('repository/trial_form.html',
                              {'forms':forms,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[5],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Outcomes Form')},
                               context_instance=RequestContext(request))


@login_required
def step_7(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    PrimaryOutcomesSet = modelformset_factory( Outcome,
                                formset=MultilingualBaseFormSet,
                                form=PrimaryOutcomesForm,extra=EXTRA_FORMS,
                                can_delete=True)
    SecondaryOutcomesSet = modelformset_factory(Outcome,
                                formset=MultilingualBaseFormSet,
                                form=SecondaryOutcomesForm,extra=EXTRA_FORMS,
                                can_delete=True)

    primary_qs = Outcome.objects.filter(trial=ct, interest=choices.OUTCOME_INTEREST[0][0])
    secondary_qs = Outcome.objects.filter(trial=ct, interest=choices.OUTCOME_INTEREST[1][0])

    if request.POST:
        primary_outcomes_formset = PrimaryOutcomesSet(request.POST, queryset=primary_qs, prefix='primary')
        secondary_outcomes_formset = SecondaryOutcomesSet(request.POST, queryset=secondary_qs, prefix='secondary')

        if primary_outcomes_formset.is_valid() and secondary_outcomes_formset.is_valid():
            outcomes = primary_outcomes_formset.save(commit=False)
            outcomes += secondary_outcomes_formset.save(commit=False)

            for outcome in outcomes:
                outcome.trial = ct

            primary_outcomes_formset.save()
            secondary_outcomes_formset.save()
            return HttpResponseRedirect(reverse('step_7',args=[trial_pk]))
    else:
        primary_outcomes_formset = PrimaryOutcomesSet(queryset=primary_qs, prefix='primary')
        secondary_outcomes_formset = SecondaryOutcomesSet(queryset=secondary_qs, prefix='secondary')

    formsets = [primary_outcomes_formset,secondary_outcomes_formset]
    return render_to_response('repository/trial_form.html',
                              {'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[6],
                               'steps': step_list(trial_pk),
                               'next_form_title':_('Descriptor Form')},
                               context_instance=RequestContext(request))


@login_required
def step_8(request, trial_pk):
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))

    contact_type = {
        'PublicContact': (PublicContact,PublicContactForm),
        'ScientificContact': (ScientificContact,ScientificContactForm),
        'SiteContact': (SiteContact,SiteContactForm)
    }

    InlineFormSetClasses = []
    for model,form in contact_type.values():
        InlineFormSetClasses.append(
            inlineformset_factory(ClinicalTrial,model,form=form,can_delete=True,extra=EXTRA_FORMS)
        )

    ContactFormSet = modelformset_factory(Contact, form=ContactForm, extra=1)

    contact_qs = Contact.objects.none()

    if request.POST:
        inlineformsets = [fs(request.POST,instance=ct) for fs in InlineFormSetClasses]
        new_contact_formset = ContactFormSet(request.POST,queryset=contact_qs)

        if not False in [fs.is_valid() for fs in inlineformsets] \
                and new_contact_formset.is_valid():

            for contactform in new_contact_formset.forms:
                if contactform.cleaned_data:
                    Relation = contact_type[contactform.cleaned_data.pop('relation')][0]
                    new_contact = contactform.save()
                    Relation.objects.create(trial=ct,contact=new_contact)

            for fs in inlineformsets:
                fs.save()
            return HttpResponseRedirect(reverse('step_8',args=[trial_pk]))
    else:
        inlineformsets = [fs(instance=ct) for fs in InlineFormSetClasses]
        new_contact_formset = ContactFormSet(queryset=contact_qs)

    formsets = inlineformsets + [new_contact_formset]
    return render_to_response('repository/trial_form.html',
                              {'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[7],
                               'steps': step_list(trial_pk)},
                               context_instance=RequestContext(request))

@login_required
def step_9(request, trial_pk):
    # TODO: this function should be on another place
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))
    su = Submission.objects.get(trial=ct)
                                             
    NewAttachmentFormSet = modelformset_factory(Attachment,
                                             extra=1,
                                             can_delete=False,
                                             form=NewAttachmentForm)

    existing_attachments = Attachment.objects.filter(submission=su)

    if request.method == 'POST':
        new_attachment_formset = NewAttachmentFormSet(request.POST,
                                                      request.FILES,
                                                      prefix='new')

        if new_attachment_formset.is_valid():
            new_attachments = new_attachment_formset.save(commit=False)

            for attachment in new_attachments:
                attachment.submission = su

            new_attachment_formset.save()
            return HttpResponseRedirect(reverse('step_9',args=[trial_pk]))
    else:
        new_attachment_formset = NewAttachmentFormSet(queryset=Attachment.objects.none(),
                                                      prefix='new')

    formsets = [new_attachment_formset]
    return render_to_response('repository/attachments.html',
                              {'formsets':formsets,
                               'existing_attachments':existing_attachments,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[8],
                               'host': request.get_host(),
                               'steps': step_list(trial_pk)},
                               context_instance=RequestContext(request))

def list_all(request, page=0, **kwargs):

    q = request.GET.get('q', '')

    if q:
        queryset = ClinicalTrial.objects.filter(Q(scientific_title__contains=q)
                                               |Q(public_title__contains=q))
    else:
        queryset = ClinicalTrial.objects.all()

    return object_list(
                  request,
                  queryset = queryset,
                  paginate_by = getattr(settings, 'PAGINATOR_CT_PER_PAGE', 10),
                  page = page,
                  extra_context = {'q': q,},
                  **kwargs)

