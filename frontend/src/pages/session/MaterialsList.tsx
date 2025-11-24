import React, { useState } from "react";
import SessionBackButton from "./SessionBackButton";
import {
  FileText,
  Archive,
  FileType,
  Presentation,
  Paperclip,
  Download,
} from "lucide-react";

interface Material {
  id: string;
  name: string;
  size: string;
  uploadedBy: string;
  uploadedAt: string;
  sessionName: string;
  type: string;
  downloadCount: number;
}

const MaterialsList: React.FC = () => {
  const [materials] = useState<Material[]>([
    {
      id: "1",
      name: "Bai_giang_Python_co_ban.pdf",
      size: "2.5 MB",
      uploadedBy: "TS. Nguyễn Văn A",
      uploadedAt: "2025-11-15 10:30:00",
      sessionName: "Session 1 - Giới thiệu Python",
      type: "pdf",
      downloadCount: 25,
    },
    {
      id: "2",
      name: "Code_demo_OOP.zip",
      size: "1.2 MB",
      uploadedBy: "TS. Trần Thị B",
      uploadedAt: "2025-11-16 14:20:00",
      sessionName: "Session 2 - OOP trong Python",
      type: "zip",
      downloadCount: 18,
    },
    {
      id: "3",
      name: "Slide_Data_Structures.pptx",
      size: "3.8 MB",
      uploadedBy: "TS. Lê Văn C",
      uploadedAt: "2025-11-17 09:15:00",
      sessionName: "Session 3 - Cấu trúc dữ liệu",
      type: "pptx",
      downloadCount: 32,
    },
  ]);

  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "pdf":
        return <FileText className="h-5 w-5" />;
      case "zip":
      case "rar":
        return <Archive className="h-5 w-5" />;
      case "doc":
      case "docx":
        return <FileType className="h-5 w-5" />;
      case "ppt":
      case "pptx":
        return <Presentation className="h-5 w-5" />;
      default:
        return <Paperclip className="h-5 w-5" />;
    }
  };

  const filteredMaterials = materials.filter((material) => {
    const matchesSearch =
      material.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      material.sessionName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || material.type === filterType;
    return matchesSearch && matchesType;
  });

  const handleDownload = (material: Material) => {
    // Simulate download
    console.log("Downloading:", material.name);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <SessionBackButton className="mb-6" />
      <h1 className="text-3xl font-bold text-gray-900 mb-6">
        Tài liệu học tập
      </h1>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tìm kiếm
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm theo tên tài liệu hoặc session..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label
              htmlFor="file-type-filter"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Loại file
            </label>
            <select
              id="file-type-filter"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Tất cả</option>
              <option value="pdf">PDF</option>
              <option value="zip">ZIP</option>
              <option value="pptx">PowerPoint</option>
              <option value="docx">Word</option>
            </select>
          </div>
        </div>
      </div>

      {/* Materials List */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Danh sách tài liệu ({filteredMaterials.length})
          </h2>
          <button className="text-blue-600 hover:text-blue-700 font-semibold">
            Tải tất cả
          </button>
        </div>

        <div className="space-y-3">
          {filteredMaterials.map((material) => (
            <div
              key={material.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
            >
              <div className="flex items-center gap-4 flex-1">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  {getFileIcon(material.type)}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {material.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-1">
                    {material.sessionName}
                  </p>
                  <p className="text-sm text-gray-500">
                    {material.size} • Bởi {material.uploadedBy} •{" "}
                    {material.uploadedAt}
                  </p>
                  <p className="text-sm text-gray-500">
                    📥 {material.downloadCount} lượt tải
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDownload(material)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold inline-flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Tải về
              </button>
            </div>
          ))}

          {filteredMaterials.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              Không tìm thấy tài liệu nào
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MaterialsList;
