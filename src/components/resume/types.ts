// Resume type definitions shared across resume components
export interface Resume {
  id?: number;
  user_id?: number;
  title?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  website?: string;
  professional_summary?: string;
  template?: string;
  photo_url?: string;
  
  // Arrays
  work_experiences?: WorkExperience[];
  education?: Education[];
  skills?: Skill[];
  projects?: Project[];
  certificates?: Certificate[];
  achievements?: Achievement[];
  languages?: Language[];
  references?: Reference[];
  
  // Customization
  font_family?: string;
  color_theme?: string;
  layout?: string;
  accent_color?: string;
  accent?: string;
  picture_style?: string;
  show_icons?: boolean;
  background_type?: string;
  section_divider?: string;
  header_shape?: string;
  icon_style?: string;
  font_size?: number;
  heading_size?: number;
  
  // Metadata
  created_at?: string;
  updated_at?: string;
}

export interface WorkExperience {
  id?: number;
  resume_id?: number;
  position: string;
  company: string;
  location?: string;
  start_date: string;
  end_date: string;
  is_current?: boolean;
  description?: string;
  responsibilities?: string[];
  bullet_points?: string[];
  achievements?: string[];
  order?: number;
}

export interface Education {
  id?: number;
  resume_id?: number;
  degree: string;
  field_of_study?: string;
  institution: string;
  school?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  description?: string;
  order?: number;
}

export interface Skill {
  id?: number;
  resume_id?: number;
  name: string;
  category?: string;
  proficiency_level?: string;
  years_of_experience?: number;
  order?: number;
}

export interface Project {
  id?: number;
  resume_id?: number;
  title?: string;
  name?: string;
  description?: string;
  technologies?: string[];
  url?: string;
  github_url?: string;
  start_date?: string;
  end_date?: string;
  order?: number;
}

export interface Certificate {
  id?: number;
  resume_id?: number;
  name: string;
  issuing_organization?: string;
  issuer?: string;
  issue_date?: string;
  date?: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
  order?: number;
}

export interface Achievement {
  id?: number;
  resume_id?: number;
  title: string;
  description?: string;
  date?: string;
  issuer?: string;
  order?: number;
}

export interface Language {
  id?: number;
  resume_id?: number;
  name: string;
  proficiency?: string;
  level?: string;
  order?: number;
}

export interface Reference {
  id?: number;
  resume_id?: number;
  name: string;
  position?: string;
  company?: string;
  email?: string;
  phone?: string;
  relationship?: string;
  order?: number;
}
