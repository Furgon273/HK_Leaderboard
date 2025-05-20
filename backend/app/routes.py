from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    create_refresh_token
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import db, User, UserProfile, Challenge, Run, Discussion, Comment
from .extensions import socketio
from functools import wraps

bp = Blueprint('main', __name__)

def admin_required(fn):
    @jwt_required()
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
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
    current_user = get_jwt_identity()
    requesting_user = User.query.filter_by(username=current_user).first()
    
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
    requesting_user = User.query.filter_by(username=current_user_identity).first()

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
    current_user = get_jwt_identity()
    requesting_user = User.query.filter_by(username=current_user).first()

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
        "runs": [{
            "id": run.id,
            "challenge": run.challenge.name,
            "status": run.status,
            "submitted_at": run.submitted_at.isoformat()
        } for run in user.runs],
        "discussions": [{
            "id": disc.id,
            "title": disc.title,
            "created_at": disc.created_at.isoformat()
        } for disc in user.discussions]
    })

@bp.route('/api/profile/me', methods=['PUT', 'PATCH'])
@jwt_required()
def update_my_profile():
    """Updates the profile of the currently authenticated user."""
    current_user_identity = get_jwt_identity()
    user = User.query.filter_by(username=current_user_identity).first()

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
        approved_runs = [run for run in user.runs if run.status == 'approved']
        if approved_runs:
            max_difficulty = max(run.challenge.difficulty for run in approved_runs)
            league = approved_runs[0].challenge.league
            ranked_users.append({
                "username": user.username,
                "max_difficulty": max_difficulty,
                "league": league,
                "runs_count": len(approved_runs)
            })
    
    ranked_users.sort(key=lambda x: (-x['max_difficulty'], -x['runs_count']))
    return jsonify(ranked_users)

@bp.route('/api/runs', methods=['GET'])
def get_runs():
    limit = request.args.get('limit', default=5, type=int)
    runs = Run.query.order_by(Run.submitted_at.desc()).limit(limit).all()
    return jsonify([{
        'id': run.id,
        'username': run.player.username,
        'challenge': run.challenge.name,
        'status': run.status,
        'submitted_at': run.submitted_at.isoformat()
    } for run in runs])

@bp.route('/api/runs', methods=['POST'])
@jwt_required()
def submit_run():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    data = request.get_json()
    challenge = Challenge.query.get(data['challenge_id'])
    if not challenge:
        return jsonify({"msg": "Challenge not found"}), 404
    
    new_run = Run(
        user_id=user.id,
        challenge_id=challenge.id,
        video_url=data['video_url'],
        description=data.get('description', '')
    )
    db.session.add(new_run)
    db.session.commit()
    
    return jsonify({
        "msg": "Run submitted for moderation",
        "run_id": new_run.id
    }), 201

@bp.route('/api/runs/<int:run_id>/approve', methods=['POST'])
@admin_required
def approve_run(run_id):
    run = Run.query.get_or_404(run_id)
    run.status = 'approved'
    run.approved_at = datetime.utcnow()
    db.session.commit()
    
    socketio.emit('run_approved', {
        'user_id': run.user_id,
        'run_id': run.id,
        'challenge': run.challenge.name
    }, room=f'user_{run.user_id}')
    
    return jsonify({"msg": "Run approved"})

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
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
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
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
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

@bp.route('/api/challenges', methods=['GET'])
def get_challenges():
    challenges = Challenge.query.all()
    return jsonify([{
        'id': challenge.id,
        'name': challenge.name,
        'description': challenge.description,
        'difficulty': challenge.difficulty,
        'league': challenge.league
    } for challenge in challenges])

@bp.route('/api/challenges', methods=['POST'])
@jwt_required()
@admin_required
def create_challenge():
    """Creates a new challenge (Admin only)."""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    difficulty = data.get('difficulty')
    league = data.get('league')

    if not name or not description or difficulty is None or not league:
        return jsonify({"message": "Missing required challenge fields"}), 400

    try:
        new_challenge = Challenge(
            name=name,
            description=description,
            difficulty=difficulty,
            league=league
        )
        db.session.add(new_challenge)
        db.session.commit()
        return jsonify({"message": "Challenge created successfully", "challenge_id": new_challenge.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while creating challenge", "error": str(e)}), 500

@bp.route('/api/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """Gets a single challenge by ID."""
    # get_or_404 automatically returns a 404 if the challenge is not found
    challenge = Challenge.query.get_or_404(challenge_id)
    return jsonify({
        'id': challenge.id,
        'name': challenge.name,
        'description': challenge.description,
        'difficulty': challenge.difficulty,
        'league': challenge.league})

@bp.route('/api/challenges/<int:challenge_id>', methods=['DELETE'])
@admin_required
def delete_challenge(challenge_id):
    """Deletes a challenge by ID (Admin only)."""
    try:
        # get_or_404 automatically returns a 404 if the challenge is not found
        challenge = Challenge.query.get_or_404(challenge_id)
        
        db.session.delete(challenge)
        db.session.commit()
        
        return jsonify({"message": f"Challenge {challenge_id} deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while deleting challenge", "error": str(e)}), 500
