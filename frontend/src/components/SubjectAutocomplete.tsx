import React, { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';

interface Subject {
    subject_id: number;
    subject_code: string;
    subject_name: string;
    department: string;
}

interface SubjectAutocompleteProps {
    subjects: Subject[];
    selectedSubject: string;
    onSelect: (subjectId: string) => void;
    registeredSubjectIds: Set<number>;
    disabled?: boolean;
}

const SubjectAutocomplete: React.FC<SubjectAutocompleteProps> = ({
    subjects,
    selectedSubject,
    onSelect,
    registeredSubjectIds,
    disabled = false
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [showDropdown, setShowDropdown] = useState(false);
    const [filteredSubjects, setFilteredSubjects] = useState<Subject[]>([]);
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Find selected subject name
    const selectedSubjectObj = subjects.find(s => s.subject_id.toString() === selectedSubject);
    const displayText = selectedSubjectObj
        ? `${selectedSubjectObj.subject_code} - ${selectedSubjectObj.subject_name}`
        : '';

    // Filter subjects based on search term
    useEffect(() => {
        if (!searchTerm.trim()) {
            setFilteredSubjects(subjects.slice(0, 10)); // Show first 10 by default
            return;
        }

        const term = searchTerm.toLowerCase();
        const filtered = subjects.filter(subject => {
            const isRegistered = registeredSubjectIds.has(subject.subject_id);
            if (isRegistered) return false;

            const codeMatch = subject.subject_code.toLowerCase().includes(term);
            const nameMatch = subject.subject_name.toLowerCase().includes(term);

            return codeMatch || nameMatch;
        }).slice(0, 20); // Limit to 20 results

        setFilteredSubjects(filtered);
    }, [searchTerm, subjects, registeredSubjectIds]);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (subject: Subject) => {
        onSelect(subject.subject_id.toString());
        setSearchTerm('');
        setShowDropdown(false);
    };

    const handleClear = () => {
        onSelect('');
        setSearchTerm('');
        setShowDropdown(false);
    };

    const handleInputFocus = () => {
        if (!selectedSubject) {
            setShowDropdown(true);
        }
    };

    return (
        <div ref={wrapperRef} className="relative">
            {/* Display selected subject */}
            {selectedSubject ? (
                <div className="flex items-center gap-2 px-3 py-2 border border-green-500 bg-green-50 rounded-md">
                    <span className="flex-1 text-sm font-medium text-green-800">
                        {displayText}
                    </span>
                    {!disabled && (
                        <button
                            type="button"
                            onClick={handleClear}
                            className="text-green-600 hover:text-green-800"
                        >
                            <X size={18} />
                        </button>
                    )}
                </div>
            ) : (
                <>
                    {/* Search input */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value);
                                setShowDropdown(true);
                            }}
                            onFocus={handleInputFocus}
                            placeholder="Tìm kiếm môn học... (VD: giải tích, MT1003)"
                            className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={disabled}
                        />
                    </div>

                    {/* Dropdown suggestions */}
                    {showDropdown && filteredSubjects.length > 0 && (
                        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                            {filteredSubjects.map((subject) => {
                                const isRegistered = registeredSubjectIds.has(subject.subject_id);

                                return (
                                    <button
                                        key={subject.subject_id}
                                        type="button"
                                        onClick={() => !isRegistered && handleSelect(subject)}
                                        disabled={isRegistered}
                                        className={`w-full text-left px-4 py-2 hover:bg-blue-50 border-b border-gray-100 last:border-b-0 ${isRegistered ? 'bg-gray-100 cursor-not-allowed opacity-50' : 'cursor-pointer'
                                            }`}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1">
                                                <div className="font-medium text-sm text-gray-900">
                                                    {subject.subject_code}
                                                </div>
                                                <div className="text-sm text-gray-600 mt-0.5">
                                                    {subject.subject_name}
                                                </div>
                                                <div className="text-xs text-gray-500 mt-0.5">
                                                    {subject.department}
                                                </div>
                                            </div>
                                            {isRegistered && (
                                                <span className="text-xs text-red-600 font-medium ml-2">
                                                    Đã đăng ký
                                                </span>
                                            )}
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                    )}

                    {/* No results message */}
                    {showDropdown && searchTerm && filteredSubjects.length === 0 && (
                        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg p-4 text-center text-gray-500">
                            Không tìm thấy môn học phù hợp
                        </div>
                    )}
                </>
            )}

            {/* Helper text */}
            <p className="text-sm text-gray-500 mt-1">
                {selectedSubject
                    ? 'Click vào X để chọn môn khác'
                    : 'Nhập tên hoặc mã môn học để tìm kiếm'
                }
            </p>
        </div>
    );
};

export default SubjectAutocomplete;
