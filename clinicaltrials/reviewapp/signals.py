from django.utils.translation import ugettext_lazy as _

def create_user_profile(sender, instance,**kwargs):
    from reviewapp.models import UserProfile
    UserProfile.objects.get_or_create(user=instance)

STEP_STATES = [
    (1, _('REMARK')),
    (2, _('MISSING')),
    (3, _('PARTIAL')),
    (4, _('COMPLETE'))
]

REMARK = STEP_STATES[0][0]
MISSING = STEP_STATES[1][0]
PARTIAL = STEP_STATES[2][0]
COMPLETE = STEP_STATES[3][0]

def check_trial_fields(sender, instance,**kwargs):

    if not hasattr(instance, 'submission'):
        return
    
    from repository.trds_forms import STEP_FORM_MATRIX, TRIAL_FORMS
    from repository.models import ClinicalTrial
    import re, pickle
    from django.template.defaultfilters import slugify
    
    FIELDS = {
        TRIAL_FORMS[0]: {
            'scientific_title': {'required': True, 'type': 'text', 'poly': True},
            'scientific_acronym': {'required': False, 'type': 'text', 'poly': True},
            'scientific_acronym_expansion': {'required': False, 'type': 'text', 'poly': True},
            'public_title': {'required': False, 'type': 'text', 'poly': True},
            'acronym': {'required': False, 'type': 'text', 'poly': True},
            'acronym_expansion': {'required': False, 'type': 'text', 'poly': True}
        }, 
        TRIAL_FORMS[1]: {
            'primary_sponsor': {'required': True, 'type': 'text', 'poly': False}
        },
        TRIAL_FORMS[2]: {
            'hc_freetext': {'required': True, 'type': 'text', 'poly': True}
        },
        TRIAL_FORMS[3]: {
            'i_freetext': {'required': True, 'type': 'text', 'poly': True}, 
            'intervention_code': {'required': True, 'type': 'mult', 'poly': False, 
                                  'queryset': instance.intervention_code()}
        },
        TRIAL_FORMS[4]: {
            'recruitment_status': {'required': True, 'type': 'text', 'poly': False}, 
            'recruitment_country': {'required': True, 'type': 'mult', 'poly': False, 
                                    'queryset': instance.recruitment_country.all()}, 
            'enrollment_start_planned': {'required': True, 'type': 'text', 'poly': False}, 
            'target_sample_size': {'required': True, 'type': 'text', 'poly': False}, 
            'inclusion_criteria': {'required': True, 'type': 'text', 'poly': True}, 
            'gender': {'required': True, 'type': 'text', 'poly': False}, 
            'agemin_value': {'required': True, 'type': 'text', 'poly': False}, 
            'agemin_unit': {'required': True, 'type': 'text', 'poly': False}, 
            'agemax_value': {'required': True, 'type': 'text', 'poly': False}, 
            'agemax_unit': {'required': True, 'type': 'text', 'poly': False}, 
        },
        TRIAL_FORMS[5]: {
            'study_type': {'required': True, 'type': 'text', 'poly': False}, 
            'study_design': {'required': True, 'type': 'text', 'poly': True}, 
            'phase': {'required': True, 'type': 'text', 'poly': False},
            #'expanded_access_program': {'required': False, 'type': 'text', 'poly': False}, 
            'intervention_assignment': {'required': False, 'type': 'text', 'poly': False}, 
            'number_of_arms': {'required': False, 'type': 'text', 'poly': False},
            'masking': {'required': False, 'type': 'text', 'poly': False},
            'allocation': {'required': False, 'type': 'text', 'poly': False}
        },
        TRIAL_FORMS[6]: {},
        TRIAL_FORMS[7]: {}
    }
    
    fields_status = {}

    # attachment
    remarks = instance.submission.remark_set.filter(status='opened').filter(context=slugify(TRIAL_FORMS[8])).count()
    count = instance.submission.attachment_set.all().count()
    for lang in instance.submission.get_mandatory_languages():
        lang = lang.lower()
        if remarks > 0:
            fields_status.update({lang: {TRIAL_FORMS[8]: REMARK}})
        elif count == 0:
            fields_status.update({lang: {TRIAL_FORMS[8]: PARTIAL}})
        else:
            fields_status.update({lang: {TRIAL_FORMS[8]: COMPLETE}})

    for step, forms in STEP_FORM_MATRIX.items():
    
        step_status = {}
        
        remarks = instance.submission.remark_set.filter(status='opened').filter(context=slugify(step)).count()
        if remarks > 0:
            for lang in instance.submission.get_mandatory_languages():
                lang = lang.lower()
                step_status.update({lang: REMARK})
        else:
            for form in forms:
                if hasattr(form.Meta,'queryset'):
                    count = form.Meta.queryset.filter(trial=instance).count()
                    
                    for lang in instance.submission.get_mandatory_languages():
                        lang = lang.lower()
                        if count < form.Meta.min_required:
                            step_status.update({lang: MISSING})
                        elif count == 0:
                            if step_status.get(lang, '') != MISSING:
                                step_status.update({lang: PARTIAL})
                        else:
                            if not form.Meta.polyglot:
                                if step_status.get(lang, '') == '':
                                    step_status.update({lang: COMPLETE})
                            else:
                                for obj in form.Meta.queryset.filter(trial=instance):
                                    for field in form.Meta.polyglot_fields:
                                        if lang == 'en':
                                            value = [getattr(obj, field)]
                                        else:
                                            list_value = obj.translations.filter(language=lang)
                                            if len(list_value) > 0:
                                                value = getattr(list_value[0], field)
                                            else:
                                                value = None

                                        if value is None:
                                            if form.Meta.min_required != 0:
                                                step_status.update({lang: MISSING})
                                            else:
                                                if step_status.get(lang, '') != MISSING:
                                                    step_status.update({lang: PARTIAL})
                                        elif type(value) is str or type(value) is unicode:
                                            if re.match('^\s*$', value):
                                                if step_status.get(lang, '') != MISSING:
                                                    step_status.update({lang: MISSING})
                                                else:
                                                    if step_status.get(lang, '') != MISSING:
                                                        step_status.update({lang: PARTIAL})
                                            else:
                                                if step_status.get(lang, '') == '':
                                                    step_status.update({lang: COMPLETE})
                                        else:
                                            if len(str(value)) == 0:
                                                if form.Meta.min_required != 0:
                                                    step_status.update({lang: MISSING})
                                                else:
                                                    if step_status.get(lang, '') != MISSING:
                                                        step_status.update({lang: PARTIAL})
                                            else:
                                                if step_status.get(lang, '') == '':
                                                    step_status.update({lang: COMPLETE})
                
                else:
                    if hasattr(form.Meta,'model'):
                        if form.Meta.model == ClinicalTrial:
                            check_fields = FIELDS[step]
                            for field in form.declared_fields.keys():
                                values = {}
                                if field in check_fields.keys():
                                    if check_fields[field]['type'] == 'text':
                                        values.update({'en': getattr(instance, field)})
                                        
                                        for trans in instance.translations.all():
                                            if check_fields[field]['poly']:
                                                values.update({trans.language.lower(): getattr(trans, field)})
                                            else:
                                                values.update({trans.language.lower(): values['en']})
                                                    
                                        for lang, value in values.items():
                                            if value is None:
                                                if check_fields[field]['required']:
                                                    step_status.update({lang: MISSING})
                                                else:
                                                    if step_status.get(lang, '') != MISSING:
                                                        step_status.update({lang: PARTIAL})
                                            elif type(value) is str or type(value) is unicode:
                                                if re.match('^\s*$', value):
                                                    if check_fields[field]['required']:
                                                        step_status.update({lang: MISSING})
                                                    else:
                                                        if step_status.get(lang, '') != MISSING:
                                                            step_status.update({lang: PARTIAL})
                                                else:
                                                    if step_status.get(lang, '') == '':
                                                        step_status.update({lang: COMPLETE})
                                            else:
                                                if len(str(value)) == 0:
                                                    if check_fields[field]['required']:
                                                        step_status.update({lang: MISSING})
                                                    else:
                                                        if step_status.get(lang, '') != MISSING:
                                                            step_status.update({lang: PARTIAL})
                                                else:
                                                    if step_status.get(lang, '') == '':
                                                        step_status.update({lang: COMPLETE})
                                    
                                    else: 
                                        if check_fields[field]['type'] == 'mult':
                                            count = check_fields[field]['queryset'].count()

                                            for lang in instance.submission.get_mandatory_languages():
                                                lang = lang.lower()
                                                if count < 1:
                                                    step_status.update({lang: MISSING})
                                                else:
                                                    if step_status.get(lang, '') == '':
                                                        step_status.update({lang: COMPLETE})


        for language, status in step_status.items():
            if fields_status.get(language) is None:
                fields_status[language] = {step: status}
            else:
                fields_status[language].update({step: status})


    instance.submission.fields_status = pickle.dumps(fields_status)
    instance.submission.save()

