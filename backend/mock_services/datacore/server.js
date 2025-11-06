const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3002;

// Middleware
app.use(cors());
app.use(express.json());

// Mock student data
const mockStudents = {
  '2210001': {
    student_code: '2210001',
    full_name: 'Nguyen Van A',
    email: 'a.nguyen@hcmut.edu.vn',
    faculty: 'Computer Science',
    major: 'Software Engineering',
    year: 3,
    gpa: 3.45,
    enrolled_courses: [
      { code: 'CO3001', name: 'Software Engineering', credits: 4 },
      { code: 'CO3005', name: 'Computer Networks', credits: 4 },
      { code: 'CO3009', name: 'Database Systems', credits: 4 }
    ]
  },
  '2210002': {
    student_code: '2210002',
    full_name: 'Tran Thi B',
    email: 'b.tran@hcmut.edu.vn',
    faculty: 'Computer Science',
    major: 'Data Science',
    year: 2,
    gpa: 3.78,
    enrolled_courses: [
      { code: 'CO3001', name: 'Software Engineering', credits: 4 },
      { code: 'CO3011', name: 'Machine Learning', credits: 4 }
    ]
  }
};

// Mock course data
const mockCourses = {
  'CO3001': {
    code: 'CO3001',
    name: 'Software Engineering',
    credits: 4,
    faculty: 'Computer Science',
    semester: '232',
    instructor: 'Dr. Tran Truong Tuan Phat'
  },
  'CO3005': {
    code: 'CO3005',
    name: 'Computer Networks',
    credits: 4,
    faculty: 'Computer Science',
    semester: '232',
    instructor: 'Thac si chua tot nghiep Nguyen Thanh Nhan'
  },
  'CO3009': {
    code: 'CO3009',
    name: 'Database Systems',
    credits: 4,
    faculty: 'Computer Science',
    semester: '232',
    instructor: 'Dr. Nguyen Thi Ai Thao'
  },
  'CO3011': {
    code: 'CO3011',
    name: 'Machine Learning',
    credits: 4,
    faculty: 'Computer Science',
    semester: '232',
    instructor: 'Dr. Le Thanh Sach'
  }
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'mock-hcmut-datacore' });
});

// Get student information
app.get('/api/students/:student_code', (req, res) => {
  const { student_code } = req.params;
  const student = mockStudents[student_code];
  
  if (!student) {
    return res.status(404).json({ 
      error: 'Student not found',
      student_code 
    });
  }
  
  res.json({
    success: true,
    data: student
  });
});

// Get course information
app.get('/api/courses/:course_code', (req, res) => {
  const { course_code } = req.params;
  const course = mockCourses[course_code];
  
  if (!course) {
    return res.status(404).json({ 
      error: 'Course not found',
      course_code 
    });
  }
  
  res.json({
    success: true,
    data: course
  });
});

// Get all courses for a student
app.get('/api/students/:student_code/courses', (req, res) => {
  const { student_code } = req.params;
  const student = mockStudents[student_code];
  
  if (!student) {
    return res.status(404).json({ 
      error: 'Student not found',
      student_code 
    });
  }
  
  res.json({
    success: true,
    data: student.enrolled_courses
  });
});

// Get student GPA
app.get('/api/students/:student_code/gpa', (req, res) => {
  const { student_code } = req.params;
  const student = mockStudents[student_code];
  
  if (!student) {
    return res.status(404).json({ 
      error: 'Student not found',
      student_code 
    });
  }
  
  res.json({
    success: true,
    data: {
      student_code,
      gpa: student.gpa,
      year: student.year
    }
  });
});

// Get academic schedule
app.get('/api/students/:student_code/schedule', (req, res) => {
  const { student_code } = req.params;
  const student = mockStudents[student_code];
  
  if (!student) {
    return res.status(404).json({ 
      error: 'Student not found',
      student_code 
    });
  }
  
  // Mock schedule data
  const schedule = [
    { day: 'Monday', time: '07:30-09:30', course: 'CO3001', room: 'H1-101' },
    { day: 'Wednesday', time: '13:30-15:30', course: 'CO3005', room: 'H2-201' },
    { day: 'Friday', time: '09:30-11:30', course: 'CO3009', room: 'H3-301' }
  ];
  
  res.json({
    success: true,
    data: schedule
  });
});

// Fallback for unknown routes
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.path,
    available_endpoints: [
      'GET /health',
      'GET /api/students/:student_code',
      'GET /api/courses/:course_code',
      'GET /api/students/:student_code/courses',
      'GET /api/students/:student_code/gpa',
      'GET /api/students/:student_code/schedule'
    ]
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Mock HCMUT DataCore service running on port ${PORT}`);
});
