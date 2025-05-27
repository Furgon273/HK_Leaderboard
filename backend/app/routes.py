from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    create_refresh_token
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from .models import db, User, UserProfile, Achievement, Discussion, Comment
from .extensions import socketio
from functools import wraps

bp = Blueprint('main', __name__)

def admin_required(fn):
    @jwt_required()
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(username=current_user_identity).first_or_404()
        if not user or user.role != 'admin':
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# def moderator_required(fn):
#     @jwt_required()
#     def wrapper(*args, **kwargs):
#         current_user = get_jwt_identity()
#         user = User.query.filter_by(username=current_user).first()
#         if not user or user.role != 'moderator':
#             return jsonify({"msg": "Moderator access required"}), 403
#         return fn(*args, **kwargs)
#     return wrapper


# Добавьте обработчик для OPTIONS запросов
# @bp.route('/api/users', methods=['GET', 'OPTIONS'])
# @bp.route('/api/users/<int:user_id>/make_admin', methods=['POST', 'OPTIONS'])
# def handle_options():
#     response = jsonify({'message': 'Preflight request accepted'})
#     response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     return response

@bp.route('/api/healthcheck')
def healthcheck():
    return jsonify({"status": "healthy"}), 200

@bp.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        users = User.query.order_by(User.id).all()
        if users:
            users_info = [{'id': user.id, 'username': user.username, 'role': user.role, 'is_super_admin': user.is_super_admin} for user in users]
            return jsonify(users_info), 200
        else:
            return jsonify({"message": "No users found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching users", "error": str(e)}), 500

@bp.route('/api/users/<int:user_id>/make_admin', methods=['POST'])
@jwt_required()
def make_admin(user_id):
    current_user_identity = get_jwt_identity()
    requesting_user = User.query.filter_by(username=current_user_identity).first_or_404()
    
    # Проверяем, что текущий пользователь - админ
    if not requesting_user or not requesting_user.is_super_admin: # Assuming is_super_admin check is sufficient for make_admin
        return jsonify({"error": "Недостаточно прав"}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        user.role = 'admin'
        db.session.commit()
        return jsonify({"message": f"Пользователь {user.username} теперь администратор"})
    except Exception as e:
        db.session.rollback() # Откатываем изменения в случае ошибки
        return jsonify({"message": "An error occurred while making user admin", "error": str(e)}), 500

@bp.route('/api/users/<int:user_id>/demote', methods=['POST'])
@jwt_required()
def demote_user(user_id):
    current_user_identity = get_jwt_identity()
    requesting_user = User.query.filter_by(username=current_user_identity).first_or_404()

    # Проверяем, что текущий пользователь - супер админ
    if not requesting_user or not requesting_user.is_super_admin:
        return jsonify({"error": "Super admin access required"}), 403

    user_to_demote = User.query.get_or_404(user_id)

    if user_to_demote.is_super_admin:
        return jsonify({"error": "Cannot demote a super admin"}), 400

    try:
        user_to_demote.role = 'user'
        db.session.commit()
        return jsonify({"message": f"Пользователь {user_to_demote.username} has been demoted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while demoting user", "error": str(e)}), 500

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_identity = get_jwt_identity()
    requesting_user = User.query.filter_by(username=current_user_identity).first_or_404()

    if not requesting_user or not requesting_user.is_super_admin:
        return jsonify({"error": "Super admin access required"}), 403

    user_to_delete = User.query.get_or_404(user_id)

    if user_to_delete.is_super_admin:
        return jsonify({"error": "Cannot delete a super admin"}), 400

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({"message": f"User {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while deleting user", "error": str(e)}), 500

# @bp.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Credentials', 'true')
#     return response

@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"message": "Отсутствуют необходимые поля"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Пользователь с таким именем уже существует"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Пользователь с таким email уже существует"}), 409
    
    try:
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        new_user.set_password(password) # Используем метод set_password из модели User, который хеширует пароль
        db.session.commit() # Commit here to get the user ID

        # Создаем UserProfile для нового пользователя
        profile = UserProfile(user_id=new_user.id)
        db.session.add(profile)
 # Возможно, здесь нужно создать UserProfile, как было в оригинальном коде
        db.session.commit()
        return jsonify({"message": "Пользователь успешно зарегистрирован"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Произошла ошибка при регистрации пользователя", "error": str(e)}), 500

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"msg": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user.username)
    refresh_token = create_refresh_token(identity=user.username)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": user.username,
        "role": user.role,
        "is_super_admin": user.is_super_admin
    }), 200

@bp.route('/api/profile/<username>')
def get_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    return jsonify({
        "username": user.username,
        "bio": user.profile.bio,
        "telegram": user.profile.telegram,
        "discord": user.profile.discord,
        "avatar": user.profile.avatar_url,
        "achievements": [{"id": ach.id, "title": ach.title, "description": ach.description, "difficulty": ach.difficulty, "is_confirmed": ach.is_confirmed, "is_pending": ach.is_pending, "rejected": ach.rejected} for ach in user.achievements],
        "discussions": [{
            "id": disc.id,
            "title": disc.title,
            "created_at": disc.created_at.isoformat()
        } for disc in user.discussions]
    })

@bp.route('/api/profile/me', methods=['PUT', 'PATCH'])
@jwt_required()
def update_my_profile():
    """Updates the profile of the currently authenticated user.""" # Consider adding more comprehensive profile updates here
    current_user_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_user_identity).first_or_404()

    if not user:
        # This case should ideally not happen with jwt_required, but as a safeguard
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    try:
        profile = user.profile
        if 'telegram' in data:
            profile.telegram = data['telegram']
        if 'discord' in data:
            profile.discord = data['discord']
        if 'bio' in data:
            profile.bio = data['bio']

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating profile", "error": str(e)}), 500

@bp.route('/api/leaderboard')
def get_leaderboard():
    users = User.query.all()
    ranked_users = []

    for user in users:
        confirmed_achievements = [
            ach for ach in user.achievements if ach.is_confirmed
        ]
        
        achievement_list = [{"id": ach.id, "title": ach.title} for ach in confirmed_achievements]

        if confirmed_achievements:
            # Calculate score based on confirmed achievements
            # For example, summing up the difficulties of confirmed achievements
            total_difficulty = sum(ach.difficulty for ach in confirmed_achievements)
            ranked_users.append({
                "username": user.username,
                "score": total_difficulty, # Still include score for sorting or potential display
                "achievements": achievement_list # Include the list of confirmed achievements
            })

    # Sort users by score in descending order
    ranked_users.sort(key=lambda x: -x['score'])

    return jsonify(ranked_users)

# @bp.route('/api/runs', methods=['GET'])
# def get_runs():
#     limit = request.args.get('limit', default=5, type=int)
#     runs = Run.query.order_by(Run.submitted_at.desc()).limit(limit).all()
#     return jsonify([{
#         'id': run.id,
#         'username': run.player.username,
#         'challenge': run.challenge.name,
#         'status': run.status,
#         'submitted_at': run.submitted_at.isoformat()
#     } for run in runs])

# @bp.route('/api/runs', methods=['POST'])
# @jwt_required()
# def submit_run():
#     current_user_identity = get_jwt_identity()
#     user = User.query.filter_by(username=current_user_identity).first_or_404()
    
#     data = request.get_json()
#     challenge = Challenge.query.get(data['challenge_id'])
#     if not challenge:
#         return jsonify({"msg": "Challenge not found"}), 404
    
#     new_run = Run(
#         user_id=user.id,
#         challenge_id=challenge.id,
#         video_url=data['video_url'],
#         description=data.get('description', '')
#     )
#     db.session.add(new_run)
#     db.session.commit()
    
#     return jsonify({
#         "msg": "Run submitted for moderation",
#         "run_id": new_run.id
#     }), 201

# @bp.route('/api/runs/<int:run_id>/approve', methods=['POST'])
# @admin_required
# def approve_run(run_id):
#     run = Run.query.get_or_404(run_id)
#     run.status = 'approved'
#     run.approved_at = datetime.utcnow()
#     db.session.commit()
    
#     socketio.emit('run_approved', {
#         'user_id': run.user_id,
#         'run_id': run.id,
#         'challenge': run.challenge.name
#     }, room=f'user_{run.user_id}')
    
#     return jsonify({"msg": "Run approved"})

@bp.route('/api/discussions', methods=['GET'])  # Явно указываем GET метод
def get_discussions():
    limit = request.args.get('limit', default=5, type=int)
    discussions = Discussion.query.order_by(Discussion.created_at.desc()).limit(limit).all()
    
    return jsonify([{
        'id': discussion.id,
        'title': discussion.title,
        'author': {
            'username': discussion.author.username
        },
        'created_at': discussion.created_at.isoformat(),
        'comment_count': len(discussion.comments)
    } for discussion in discussions])

@bp.route('/api/discussions', methods=['POST'])
@jwt_required()
def create_discussion():
    current_user_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_user_identity).first_or_404()
    
    data = request.get_json()
    new_discussion = Discussion(
        title=data['title'],
        content=data['content'],
        author_id=user.id
    )
    db.session.add(new_discussion)
    db.session.commit()
    
    return jsonify({
        "msg": "Discussion created",
        "discussion_id": new_discussion.id
    }), 201

@bp.route('/api/discussions/<int:discussion_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(discussion_id):
    current_user_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_user_identity).first_or_404()
    
    data = request.get_json()
    new_comment = Comment(
        content=data['content'],
        author_id=user.id,
        discussion_id=discussion_id,
        parent_id=data.get('parent_id')
    )
    db.session.add(new_comment)
    db.session.commit()
    
    discussion = Discussion.query.get(discussion_id)
    socketio.emit('new_comment', {
        'discussion_id': discussion_id,
        'comment_id': new_comment.id,
        'author': user.username,
        'content': new_comment.content
    }, room=f'discussion_{discussion_id}')
    
    return jsonify({
        "msg": "Comment added",
        "comment_id": new_comment.id
    }), 201

# @bp.route('/api/challenges', methods=['GET'])
# def get_challenges():
#     challenges = Challenge.query.all()
#     return jsonify([{
#         'id': challenge.id,
#         'name': challenge.name,
#         'description': challenge.description,
#         'difficulty': challenge.difficulty,
#         'league': challenge.league
#     } for challenge in challenges])

# @bp.route('/api/challenges', methods=['POST'])
# @jwt_required()
# @admin_required
# def create_challenge():
#     """Creates a new challenge (Admin only).""" # Consider validation for difficulty range and league
#     data = request.get_json()
#     name = data.get('name')
#     description = data.get('description')
#     difficulty = data.get('difficulty')
#     league = data.get('league')

#     if not name or not description or difficulty is None or not league:
#         return jsonify({"message": "Missing required challenge fields"}), 400

#     try:
#         new_challenge = Challenge(
#             name=name,
#             description=description,
#             difficulty=difficulty,
#             league=league
#         )
#         db.session.add(new_challenge)
#         db.session.commit()
#         return jsonify({"message": "Challenge created successfully", "challenge_id": new_challenge.id}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": "An error occurred while creating challenge", "error": str(e)}), 500

# @bp.route('/api/challenges/<int:challenge_id>', methods=['GET'])
# def get_challenge(challenge_id):
#     """Gets a single challenge by ID."""
#     # get_or_404 automatically returns a 404 if the challenge is not found
#     challenge = Challenge.query.get_or_404(challenge_id)
#     return jsonify({
#         'id': challenge.id,
#         'name': challenge.name,
#         'description': challenge.description,
#         'difficulty': challenge.difficulty,
#         'league': challenge.league})

# @bp.route('/api/challenges/<int:challenge_id>', methods=['DELETE'])
# @admin_required
# def delete_challenge(challenge_id):
#     """Deletes a challenge by ID (Admin only)."""
#     try:
#         # get_or_404 automatically returns a 404 if the challenge is not found
#         challenge = Challenge.query.get_or_404(challenge_id)
        
#         db.session.delete(challenge)
#         db.session.commit()
        
#         return jsonify({"message": f"Challenge {challenge_id} deleted successfully"}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": "An error occurred while deleting challenge", "error": str(e)}), 500

@bp.route('/api/achievements', methods=['GET'])
@jwt_required() # Assuming you want this route to be protected
def get_achievements():
    """Gets all achievements."""
    try:
        achievements = Achievement.query.all()
        achievements_data = [{
            'id': ach.id,
            'title': ach.title,
            'description': ach.description,
            'difficulty': ach.difficulty,
            'link': ach.link,
            'is_confirmed': ach.is_confirmed,
            'is_pending': ach.is_pending,
            'username': ach.user.username # Include username for display
        } for ach in achievements]
        return jsonify(achievements_data), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching achievements", "error": str(e)}), 500


@bp.route('/api/achievements', methods=['POST'])
@jwt_required()
def submit_achievement():
    current_user_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_user_identity).first_or_404()

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    difficulty = data.get('difficulty')
    link = data.get('link')

    if not title or difficulty is None:
        return jsonify({"message": "Missing required achievement fields (title, difficulty)"}), 400

    try:
        new_achievement = Achievement(
            user_id=user.id,
            title=title,
            description=description,
            difficulty=difficulty,
            link=link,
            is_confirmed=False,
            is_pending=True
        )
        db.session.add(new_achievement)
        db.session.commit()
        return jsonify({"message": "Achievement submitted for review", "achievement_id": new_achievement.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while submitting achievement", "error": str(e)}), 500

@bp.route('/api/achievements/<int:achievement_id>/confirm', methods=['POST'])
@admin_required
def confirm_achievement(achievement_id):
    # Allow confirming achievements regardless of their previous state
    achievement = Achievement.query.get_or_404(achievement_id)

    try:
        achievement.is_confirmed = True
        achievement.is_pending = False
        achievement.rejected = False
        db.session.commit()
        return jsonify({"message": "Achievement confirmed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while confirming achievement", "error": str(e)}), 500

@bp.route('/api/achievements/<int:achievement_id>/reject', methods=['POST'])
@admin_required
def reject_achievement(achievement_id):
    """Rejects a pending achievement by ID (Admin only)."""
    achievement = Achievement.query.get_or_404(achievement_id)
    try:
        achievement.is_confirmed = False # Ensure it's not confirmed if rejected
        achievement.is_pending = False
        achievement.rejected = True
        db.session.commit()
        return jsonify({"message": "Achievement rejected successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while rejecting achievement", "error": str(e)}), 500

@bp.route('/api/achievements/pending', methods=['GET'])
@admin_required
def get_pending_achievements():
    """Gets all pending achievements (Admin only)."""
    try:
        achievements = Achievement.query.filter_by(is_pending=True).all()
        return jsonify([{
            'id': ach.id,
            'title': ach.title,
            'description': ach.description,
            'difficulty': ach.difficulty,
            'link': ach.link,
            'username': ach.user.username # Include username for display
        } for ach in achievements]), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching pending achievements", "error": str(e)}), 500

@bp.route('/api/achievements/confirmed', methods=['GET'])
@admin_required
def get_confirmed_achievements():
    """Gets all confirmed achievements (Admin only)."""
    try:
        achievements = Achievement.query.filter_by(is_confirmed=True, is_pending=False).all()
        return jsonify([{
            'id': ach.id,
            'title': ach.title,
            'description': ach.description,
            'difficulty': ach.difficulty,
            'link': ach.link,
            'username': ach.user.username # Include username for display
        } for ach in achievements]), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching confirmed achievements", "error": str(e)}), 500

@bp.route('/api/achievements/<int:achievement_id>', methods=['GET'])
@jwt_required() # Assuming you want this route to be protected for fetching single achievement
def get_achievement(achievement_id):
    """Gets a single achievement by ID."""
    try:
        achievement = Achievement.query.get(achievement_id)
        if not achievement:
            return jsonify({"message": "Achievement not found"}), 404
        
        return jsonify({
            'id': achievement.id,
            'title': achievement.title,
            'description': achievement.description,
            'difficulty': achievement.difficulty,
            'link': achievement.link,
            'is_confirmed': achievement.is_confirmed,
            'is_pending': achievement.is_pending,
            'rejected': achievement.rejected
        }), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching achievement", "error": str(e)}), 500

@bp.route('/api/achievements/<int:achievement_id>', methods=['PUT'])
@jwt_required() # Assuming users who own the achievement can also update
def update_achievement(achievement_id):
    """Updates an achievement by ID. Accessible to admin or achievement owner."""
    achievement = Achievement.query.get_or_404(achievement_id)
    data = request.get_json()

    current_user_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_user_identity).first_or_404()

    # Check if the current user is an admin or the achievement owner
    if not user.role == 'admin' and user.id != achievement.user_id:
         return jsonify({"message": "You do not have permission to update this achievement"}), 403

    try:
        achievement.title = data.get('title', achievement.title)
        achievement.description = data.get('description', achievement.description)
        achievement.difficulty = data.get('difficulty', achievement.difficulty)
        achievement.link = data.get('link', achievement.link)

        # Reset status to pending when the achievement is updated
        achievement.is_confirmed = False
        achievement.is_pending = True
        achievement.rejected = False

        db.session.commit()
        return jsonify({"message": "Achievement updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while updating achievement", "error": str(e)}), 500

@bp.route('/api/achievements/<int:achievement_id>', methods=['DELETE'])
@admin_required
def delete_achievement(achievement_id):
    """Deletes an achievement by ID (Admin only)."""
    try:
        achievement = Achievement.query.get_or_404(achievement_id)
        db.session.delete(achievement)
        db.session.commit()
        return jsonify({"message": f"Achievement {achievement_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while deleting achievement", "error": str(e)}), 500
