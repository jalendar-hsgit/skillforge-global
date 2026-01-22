"""
Style Settings Service - Handles all resume styling with database tracking
Tracks every style change without breaking existing code
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import insert
from app.modelsx.resume import Resume
import json
import logging

logger = logging.getLogger(__name__)

class StyleSettingsService:
    """Service for managing resume style settings with full audit trail"""
    
    # Mapping of style fields to database columns
    STYLE_FIELDS = {
        'font_family': 'font_family',
        'color_theme': 'color_theme',
        'picture_style': 'picture_style',
        'layout': 'layout',
        'accent_color': 'accent_color',
        'text_color': 'text_color',
        'heading_color': 'heading_color',
        'line_spacing': 'line_spacing',
        'font_size': 'font_size',
        'heading_size': 'heading_size',
        'show_icons': 'show_icons',
        'background_type': 'background_type',
        'section_divider': 'section_divider',
        'header_shape': 'header_shape',
        'icon_style': 'icon_style',
    }
    
    # Default style values
    DEFAULTS = {
        'font_family': 'Roboto',
        'color_theme': 'blue',
        'picture_style': 'circle',
        'layout': 'single-column',
        'accent_color': '#2563eb',
        'text_color': '#000000',
        'heading_color': '#1f2937',
        'line_spacing': 1.2,
        'font_size': 11,
        'heading_size': 14,
        'show_icons': True,
        'background_type': 'none',
        'section_divider': 'line',
        'header_shape': 'default',
        'icon_style': 'default',
    }
    
    @staticmethod
    def get_style_settings(resume: Resume) -> Dict[str, Any]:
        """Get all current style settings for a resume"""
        return {
            'font_family': resume.font_family or StyleSettingsService.DEFAULTS['font_family'],
            'color_theme': resume.color_theme or StyleSettingsService.DEFAULTS['color_theme'],
            'picture_style': resume.picture_style or StyleSettingsService.DEFAULTS['picture_style'],
            'layout': resume.layout or StyleSettingsService.DEFAULTS['layout'],
            'accent_color': resume.accent_color or StyleSettingsService.DEFAULTS['accent_color'],
            'text_color': resume.text_color or StyleSettingsService.DEFAULTS['text_color'],
            'heading_color': resume.heading_color or StyleSettingsService.DEFAULTS['heading_color'],
            'line_spacing': resume.line_spacing or StyleSettingsService.DEFAULTS['line_spacing'],
            'font_size': resume.font_size or StyleSettingsService.DEFAULTS['font_size'],
            'heading_size': resume.heading_size or StyleSettingsService.DEFAULTS['heading_size'],
            'show_icons': resume.show_icons if resume.show_icons is not None else StyleSettingsService.DEFAULTS['show_icons'],
            'background_type': resume.background_type or StyleSettingsService.DEFAULTS['background_type'],
            'section_divider': getattr(resume, 'section_divider', StyleSettingsService.DEFAULTS.get('section_divider')),
            'header_shape': getattr(resume, 'header_shape', StyleSettingsService.DEFAULTS.get('header_shape')),
            'icon_style': getattr(resume, 'icon_style', StyleSettingsService.DEFAULTS.get('icon_style')),
        }
    
    @staticmethod
    def update_style_settings(
        resume_id: int, 
        user_id: int,
        updates: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Update style settings and track all changes
        Non-destructive: Only updates provided fields, keeps existing values
        """
        try:
            # Get current resume
            resume = db.query(Resume).filter(
                Resume.id == resume_id,
                Resume.user_id == user_id
            ).first()
            
            if not resume:
                logger.error(f"Resume {resume_id} not found for user {user_id}")
                return {"error": "Resume not found"}
            
            # Get current style settings
            old_settings = StyleSettingsService.get_style_settings(resume)
            
            # Prepare update history
            update_history = resume.style_settings_history or {}
            if not isinstance(update_history, dict):
                update_history = {}
            
            # Track changes
            changes = []
            
            # Update each field that was provided
            for field, value in updates.items():
                if field not in StyleSettingsService.STYLE_FIELDS:
                    continue
                
                db_column = StyleSettingsService.STYLE_FIELDS[field]
                old_value = getattr(resume, db_column, None)
                
                if old_value != value:
                    # Record the change
                    changes.append({
                        'field': field,
                        'old_value': str(old_value),
                        'new_value': str(value),
                        'changed_at': datetime.utcnow().isoformat()
                    })
                    
                    # Update the resume
                    setattr(resume, db_column, value)
                    logger.info(f"Resume {resume_id}: {field} changed from {old_value} to {value}")
            
            # Update tracking timestamps and history
            if changes:
                resume.style_settings_updated_at = datetime.utcnow()
                
                # Add to history
                if 'history' not in update_history:
                    update_history['history'] = []
                
                update_history['history'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'changes': changes
                })
                
                # Keep only last 50 changes for storage efficiency
                if len(update_history['history']) > 50:
                    update_history['history'] = update_history['history'][-50:]
                
                resume.style_settings_history = update_history
            
            # Commit changes
            db.commit()
            db.refresh(resume)
            
            # Get new settings
            new_settings = StyleSettingsService.get_style_settings(resume)
            
            return {
                'success': True,
                'resume_id': resume_id,
                'changes': changes,
                'old_settings': old_settings,
                'new_settings': new_settings,
                'timestamp': resume.style_settings_updated_at.isoformat() if resume.style_settings_updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error updating style settings: {e}")
            db.rollback()
            return {
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def get_style_history(resume_id: int, user_id: int, db: Session) -> Dict[str, Any]:
        """Get the complete style change history for a resume"""
        try:
            resume = db.query(Resume).filter(
                Resume.id == resume_id,
                Resume.user_id == user_id
            ).first()
            
            if not resume:
                return {"error": "Resume not found"}
            
            history = resume.style_settings_history or {}
            
            return {
                'resume_id': resume_id,
                'last_updated': resume.style_settings_updated_at.isoformat() if resume.style_settings_updated_at else None,
                'total_changes': len(history.get('history', [])),
                'change_history': history.get('history', []),
                'current_settings': StyleSettingsService.get_style_settings(resume)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving style history: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def reset_to_defaults(resume_id: int, user_id: int, db: Session) -> Dict[str, Any]:
        """Reset all style settings to defaults and record in history"""
        try:
            resume = db.query(Resume).filter(
                Resume.id == resume_id,
                Resume.user_id == user_id
            ).first()
            
            if not resume:
                return {"error": "Resume not found"}
            
            # Record old settings before reset
            old_settings = StyleSettingsService.get_style_settings(resume)
            
            # Reset all to defaults
            for field, default_value in StyleSettingsService.DEFAULTS.items():
                db_column = StyleSettingsService.STYLE_FIELDS.get(field)
                if db_column:
                    setattr(resume, db_column, default_value)
            
            # Update history
            update_history = resume.style_settings_history or {}
            if not isinstance(update_history, dict):
                update_history = {}
            
            if 'history' not in update_history:
                update_history['history'] = []
            
            update_history['history'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'reset_to_defaults',
                'old_settings': old_settings
            })
            
            resume.style_settings_updated_at = datetime.utcnow()
            resume.style_settings_history = update_history
            
            db.commit()
            db.refresh(resume)
            
            return {
                'success': True,
                'message': 'All styles reset to defaults',
                'new_settings': StyleSettingsService.get_style_settings(resume)
            }
            
        except Exception as e:
            logger.error(f"Error resetting styles: {e}")
            db.rollback()
            return {"error": str(e)}
    
    @staticmethod
    def validate_style_update(updates: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate style update values"""
        # Validate font sizes
        if 'font_size' in updates:
            if not (8 <= updates['font_size'] <= 16):
                return False, "Font size must be between 8 and 16"
        
        if 'heading_size' in updates:
            if not (9 <= updates['heading_size'] <= 24):
                return False, "Heading size must be between 9 and 24"
        
        # Validate line spacing
        if 'line_spacing' in updates:
            if not (1.0 <= updates['line_spacing'] <= 2.0):
                return False, "Line spacing must be between 1.0 and 2.0"
        
        # Validate colors (hex format)
        import re
        hex_color_pattern = re.compile(r'^#[0-9A-F]{6}$', re.IGNORECASE)
        
        for color_field in ['accent_color', 'text_color', 'heading_color']:
            if color_field in updates:
                if not hex_color_pattern.match(updates[color_field]):
                    return False, f"{color_field} must be valid hex color (e.g., #2563eb)"
        
        # Validate layout
        valid_layouts = ['single-column', 'two-column', 'sidebar', 'centered', 'asymmetric']
        if 'layout' in updates:
            if updates['layout'] not in valid_layouts:
                return False, f"Layout must be one of: {', '.join(valid_layouts)}"
        
        return True, None
