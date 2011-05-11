from django.shortcuts import render_to_response, get_object_or_404, redirect
from news.models import Submission, Comment
from news.forms import SubmissionForm, CommentForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def _update_session(session, key, val, coll=True):
    if key in session:
        session[key] = session[key] + [val,] if coll else val
    else:
        session[key] = [val,] if coll else val

def list(request, by_popularity=False):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            s = form.save()
            _update_session(request.session, 'submissions', s)
            return redirect('newest')
        else:
            return render_to_response('new.html', {'form': form}, context_instance=RequestContext(request))

    return render_to_response(
            'list.html',
            {
                'submissions': getattr(Submission.objects, 'popular' if by_popularity else 'all')()
            },
            context_instance = RequestContext(request)
            )

@login_required
def create(request): 
    return render_to_response(
                'new.html',
                {'form': SubmissionForm(), },
                context_instance=RequestContext(request)
            )

def show(request, s_id):
    submission = get_object_or_404(Submission, pk=s_id)
    return render_to_response(
             'show.html',
             {'submission': submission, 'form': CommentForm(initial={'submission': submission})},
             context_instance=RequestContext(request)
            )

def upvote(request, s_id):
    submission = get_object_or_404(Submission, pk=s_id)
    submission.upvote()
    _update_session(request.session, 'votes', submission)
    return redirect(submission)

def comment(request, s_id):
    submission = get_object_or_404(Submission, pk=s_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save()
            _update_session(request.session, 'comments', c)
            return redirect(submission)
        else:
            return render_to_response('show.html', {'submission': submission, 'form': form},
                    context_instance=RequestContext(request))

def edit_comment(request, s_id, c_id):
    comment = get_object_or_404(Comment, pk=c_id)
    submission = get_object_or_404(Submission, pk=s_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            c = form.save()
            return redirect(submission)
        else:
            return render_to_response('edit_comment.html', {'form': form, 'comment':comment},
                    context_instance=RequestContext(request))

    return render_to_response('edit_comment.html',
            {'form': CommentForm(instance=comment), 'comment':comment},
            context_instance=RequestContext(request)
            )
