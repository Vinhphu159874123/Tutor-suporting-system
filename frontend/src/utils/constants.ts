// Training Programs
export const TRAINING_PROGRAMS = [
  "Đại học chính quy",
  "Chương trình tiên tiến",
  "Chương trình chất lượng cao",
  "Liên kết quốc tế",
];

// Faculty structure with majors
export const FACULTY_STRUCTURE: Record<string, { name: string; majors: string[] }> = {
  CS: {
    name: "Khoa Khoa học và Kỹ thuật Máy tính",
    majors: [
      "Khoa học Máy tính",
      "Kỹ thuật Phần mềm",
      "Hệ thống Thông tin",
      "Kỹ thuật Máy tính",
    ],
  },
  EE: {
    name: "Khoa Điện - Điện tử",
    majors: [
      "Kỹ thuật Điện",
      "Kỹ thuật Điện tử",
      "Tự động hóa",
      "Kỹ thuật Điều khiển",
    ],
  },
  ME: {
    name: "Khoa Cơ khí",
    majors: [
      "Kỹ thuật Cơ khí",
      "Kỹ thuật Cơ điện tử",
      "Kỹ thuật Nhiệt",
      "Công nghệ Vật liệu",
    ],
  },
  CE: {
    name: "Khoa Kỹ thuật Xây dựng",
    majors: [
      "Xây dựng Dân dụng",
      "Xây dựng Công nghiệp",
      "Kỹ thuật Giao thông",
      "Kỹ thuật Môi trường",
    ],
  },
  CHEM: {
    name: "Khoa Kỹ thuật Hóa học",
    majors: [
      "Kỹ thuật Hóa học",
      "Công nghệ Thực phẩm",
      "Công nghệ Môi trường",
    ],
  },
};

// Faculty options for dropdown
export const facultyOptions = Object.entries(FACULTY_STRUCTURE).map(([id, data]) => ({
  id,
  label: data.name,
}));
