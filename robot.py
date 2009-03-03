# setup the correct enivironment variables :
from django.core.management import setup_environ
import settings
setup_environ(settings)
# now continue as per usual:
import datetime, random, codecs, sys
from emocracy.emocracy_core.models import IssueBody, Votable, NewStyleVote
from django.contrib.auth.models import User

def homerus(n_issues = 10):
    users = list(User.objects.all())
    
    # read file:
    f = codecs.open("odysseus.txt", "r", "utf-8")
    paragraphs = []
    line = f.readline()
    current_par = []
    while line != "":
        line = f.readline()
        if line != "\r\n" and line != "\n":
            current_par.append(line.strip())
        else:
            if len(current_par) > 0:
                p = u" ".join(current_par)
                if not u"CHAPTER" in p:
                    paragraphs.append(p)
#                    print "-" * 40, len(current_par)
#                    print p.encode('ascii', 'replace')
            current_par = []
    f.close()
    
    # use django as a library to add lots of issues:
    for i in range(n_issues):
        par1 = random.choice(paragraphs)
        par2 = random.choice(paragraphs)
        new_issue = IssueBody(
            owner = random.choice(users),
            title = par1[0:30],
            body = par1 + u" \n\n\n" + par2,
            url = "http://whatever.nvt",
            source_type = "website",
            time_stamp = datetime.datetime.now(),
        )
        new_issue.save()
        
        new_votable = Votable.objects.create_for_object(new_issue, title = new_issue.title, owner = new_issue.owner)
        new_votable.vote(new_issue.owner, random.choice([-1, 1]), keep_private = False)    

    print n_issues, "random issue(s) were added to the system."


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            n_issues = int(sys.argv[1])
        except ValueError:
            n_issues = 10
        except: 
            raise
    else:
        n_issues = 10
    
    homerus(n_issues)