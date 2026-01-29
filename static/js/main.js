// Main JavaScript file for Modern CMS

document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');

    if (mobileBtn && mainNav) {
        mobileBtn.addEventListener('click', function () {
            mainNav.classList.toggle('active');
        });
    }

    // Alert close buttons
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', function () {
            this.closest('.alert').remove();
        });
    });

    // User dropdown menu
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.addEventListener('click', function (e) {
            e.stopPropagation();
            this.classList.toggle('open');
        });

        document.addEventListener('click', function () {
            userMenu.classList.remove('open');
        });
    }

    // Rating stars
    const ratingStars = document.querySelector('.rating-stars');
    if (ratingStars) {
        const postId = ratingStars.dataset.postId;

        ratingStars.querySelectorAll('.star-btn').forEach(star => {
            star.addEventListener('click', async function () {
                const rating = this.dataset.rating;

                try {
                    const response = await fetch(`/api/v1/posts/${postId}/rate`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ rating: parseInt(rating) })
                    });

                    if (response.ok) {
                        // Update UI
                        ratingStars.querySelectorAll('.star-btn').forEach((s, i) => {
                            if (i < rating) {
                                s.classList.add('active');
                                s.querySelector('i').classList.remove('far');
                                s.querySelector('i').classList.add('fas');
                            } else {
                                s.classList.remove('active');
                                s.querySelector('i').classList.remove('fas');
                                s.querySelector('i').classList.add('far');
                            }
                        });
                    }
                } catch (e) {
                    console.error('Rating error:', e);
                }
            });
        });
    }

    // Comment vote buttons
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', async function () {
            const commentId = this.dataset.commentId;
            const vote = this.dataset.vote;

            try {
                const response = await fetch(`/api/v1/comments/${commentId}/vote`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ vote: parseInt(vote) })
                });

                if (response.ok) {
                    const data = await response.json();
                    // Update counts
                    const parent = this.closest('.comment-actions');
                    parent.querySelector('[data-vote="1"]').innerHTML = `<i class="fas fa-thumbs-up"></i> ${data.likes}`;
                    parent.querySelector('[data-vote="-1"]').innerHTML = `<i class="fas fa-thumbs-down"></i> ${data.dislikes}`;
                }
            } catch (e) {
                console.error('Vote error:', e);
            }
        });
    });

    // Reply buttons
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const commentId = this.dataset.commentId;
            const comment = this.closest('.comment');

            // Check if form already exists
            let form = comment.querySelector('.reply-form');
            if (form) {
                form.remove();
                return;
            }

            // Create reply form
            form = document.createElement('form');
            form.className = 'reply-form';
            form.method = 'post';
            form.action = window.location.pathname.replace('/post/', '/post/').split('#')[0] + '/comment';
            form.innerHTML = `
                <input type="hidden" name="parent_id" value="${commentId}">
                <textarea name="content" placeholder="Javobingizni yozing..." required></textarea>
                <button type="submit" class="btn btn-primary btn-sm">Javob berish</button>
            `;
            form.style.cssText = 'margin-top:1rem; padding:1rem; background:var(--gray-100); border-radius:0.5rem;';

            comment.querySelector('.comment-content').appendChild(form);
        });
    });

    // Smooth scroll to comments
    if (window.location.hash === '#comments') {
        const commentsSection = document.querySelector('.comments-section');
        if (commentsSection) {
            commentsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
});
