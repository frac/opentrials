import os
from datetime import date
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def export_database(request):
    #output backup
    stdin,stdout = os.popen2(r'which mysqldump')
    stdin.close()

    mysqldump_bin = stdout.readline().replace('\n','')
    stdout.close()
    
    cmd = mysqldump_bin+' --opt --compact --skip-add-locks -u %s -p%s %s | bzip2 -c' % (settings.DATABASE_USER, settings.DATABASE_PASSWORD, settings.DATABASE_NAME)
    print cmd
    stdin, stdout = os.popen2(cmd)
    stdin.close()
    
    response = HttpResponse(stdout, mimetype="application/octet-stream")
    response['Content-Disposition'] = 'attachment; filename=%s' % date.today().__str__()+'_db.sql.bz2'
    return response

def smoke_test(request):
    from datetime import datetime
    return HttpResponse(datetime.now().strftime('%H:%M:%S'))

@user_passes_test(lambda u: u.is_staff)
def req_dump(request):
    template = '''
    <form action="./" method="POST">
    <input type="text" name="word" value="mitochondrial">
    <input type="submit" name="btn1" value="one">
    <input type="submit" name="btn2" value="two">
    </form>
    <table border="1">
       <tr><th>key</th><th>POST[key]</th></tr>
    %s
    </table>
    <hr>
    <p>
      <a href="this_is_a_broken_link">Click to test broken link notification</a>
    </p>
    '''
    rows = []
    for k in request.POST.keys():
        rows.append('<tr><th>%s</th><td>%s</td></tr>' % (k, request.POST[k]))
    return HttpResponse(template % ('\n'.join(rows)))

@user_passes_test(lambda u: u.is_staff)
def sys_info(request):
    template = u'''
    <h1>Site.objects.get_current()</h1>
    <table>
       <tr><th>id</th><td>%(site.pk)s</td></tr>
       <tr><th>domain</th><td>%(site.domain)s</td></tr>
       <tr><th>name</th><td>%(site.name)s</td></tr>
    </table>
    <h1>settings path</h1>
    <pre>%(settingspath)s</pre>
    <h1>svn info</h1>
    <pre>%(svninfo)s</pre>
    <h1>sys.path</h1>
    <pre>%(syspath)s</pre>
    '''
    import sys
    import settings
    from django.contrib.sites.models import Site
    from subprocess import Popen, PIPE
    site = Site.objects.get_current()
    svnout, svnerr = Popen(['svn', 'info', '-r', 'HEAD', settings.PROJECT_PATH], stdout=PIPE).communicate()
    svnout = svnout.decode('utf-8') if svnout else u''
    svnerr = svnerr.decode('utf-8') if svnerr else u''
    return HttpResponse(template % {'site.pk':site.pk,
                                    'site.domain':site.domain,
                                    'site.name':site.name,
                                    'settingspath': settings.PROJECT_PATH,
                                    'syspath':'\n'.join(sys.path),
                                    'svninfo':svnout + svnerr})

@user_passes_test(lambda u: u.is_staff)
def raise_error(request):
    class FakeError(StandardError):
        ''' this is just to test error e-mails and logging '''
    raise FakeError('This is not really an error')



