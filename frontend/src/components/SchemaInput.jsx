import React, { useState, useRef } from "react";
import { Database, ChevronDown, ChevronUp, Plus, X, Info, Upload, CheckCircle, AlertCircle } from "lucide-react";
import { api } from "../api";

const SchemaInput = ({ schema, onSchemaChange }) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null); // { type: 'success'|'error', message: string }
    const fileInputRef = useRef(null);

    const addTable = () => {
        const newTable = {
            name: `table_${schema.tables.length + 1}`,
            description: "",
            columns: [
                { name: "id", type: "INTEGER", primary_key: true, nullable: false }
            ],
            foreign_keys: []
        };
        onSchemaChange({
            ...schema,
            tables: [...schema.tables, newTable]
        });
    };

    const removeTable = (index) => {
        onSchemaChange({
            ...schema,
            tables: schema.tables.filter((_, i) => i !== index)
        });
    };

    const updateTable = (index, field, value) => {
        const newTables = [...schema.tables];
        newTables[index] = { ...newTables[index], [field]: value };
        onSchemaChange({ ...schema, tables: newTables });
    };

    const addColumn = (tableIndex) => {
        const newTables = [...schema.tables];
        newTables[tableIndex].columns.push({
            name: `column_${newTables[tableIndex].columns.length + 1}`,
            type: "TEXT",
            primary_key: false,
            nullable: true
        });
        onSchemaChange({ ...schema, tables: newTables });
    };

    const removeColumn = (tableIndex, columnIndex) => {
        const newTables = [...schema.tables];
        newTables[tableIndex].columns = newTables[tableIndex].columns.filter(
            (_, i) => i !== columnIndex
        );
        onSchemaChange({ ...schema, tables: newTables });
    };

    const updateColumn = (tableIndex, columnIndex, field, value) => {
        const newTables = [...schema.tables];
        newTables[tableIndex].columns[columnIndex] = {
            ...newTables[tableIndex].columns[columnIndex],
            [field]: value
        };
        onSchemaChange({ ...schema, tables: newTables });
    };

    const loadExampleSchema = () => {
        const exampleSchema = {
            name: "music_database",
            tables: [
                {
                    name: "singer",
                    description: "Information about singers",
                    columns: [
                        { name: "singer_id", type: "INTEGER", primary_key: true, nullable: false },
                        { name: "name", type: "TEXT", nullable: false },
                        { name: "birth_year", type: "INTEGER", nullable: true },
                        { name: "country", type: "TEXT", nullable: true }
                    ],
                    foreign_keys: []
                },
                {
                    name: "song",
                    description: "Songs in the database",
                    columns: [
                        { name: "song_id", type: "INTEGER", primary_key: true, nullable: false },
                        { name: "title", type: "TEXT", nullable: false },
                        { name: "singer_id", type: "INTEGER", nullable: false },
                        { name: "release_year", type: "INTEGER", nullable: true }
                    ],
                    foreign_keys: [
                        { column: "singer_id", referenced_table: "singer", referenced_column: "singer_id" }
                    ]
                }
            ]
        };
        onSchemaChange(exampleSchema);
        setUploadStatus({ type: 'success', message: 'Example schema loaded' });
        setTimeout(() => setUploadStatus(null), 3000);
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsUploading(true);
        setUploadStatus(null);

        try {
            const result = await api.extractSchemaFromFile(file);

            // Update schema with extracted data
            onSchemaChange(result.schema);

            // Show inline success message
            setUploadStatus({
                type: 'success',
                message: `Extracted ${result.info.table_count} table(s) with ${result.info.total_columns} columns from ${result.filename}`
            });

            // Auto-hide after 5 seconds
            setTimeout(() => setUploadStatus(null), 5000);

        } catch (error) {
            setUploadStatus({
                type: 'error',
                message: error.message
            });
        } finally {
            setIsUploading(false);
            // Reset file input
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    };

    return (
        <div className="border  border-slate-700 bg-slate-900/50 rounded-xl overflow-hidden">
            {/* Header */}
            <div
                className="flex items-center justify-between p-4 bg-slate-800/50 cursor-pointer hover:bg-slate-800/70 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-3">
                    <Database size={20} className="text-emerald-400" />
                    <span className="font-semibold text-slate-200">Database Schema</span>
                    <span className="text-xs text-slate-500">
                        {schema.tables.length} table{schema.tables.length !== 1 ? "s" : ""}
                    </span>
                </div>
                <div className="flex items-center gap-2">
                    {/* Hidden file input */}
                    <input
                        id="db-file-upload"
                        name="db-file-upload"
                        ref={fileInputRef}
                        type="file"
                        accept=".db,.sqlite,.sqlite3,.xlsx,.xls,.csv,.sql,.json"
                        onChange={handleFileUpload}
                        className="hidden"
                        aria-label="Upload database file"
                    />

                    {/* Upload Database Button */}
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            fileInputRef.current?.click();
                        }}
                        disabled={isUploading}
                        className="px-3 py-1 text-xs bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Upload database or data file: SQLite, Excel, CSV, SQL dump, JSON"
                    >
                        {isUploading ? (
                            <>
                                <div className="w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                                Extracting...
                            </>
                        ) : (
                            <>
                                <Upload size={14} />
                                Upload DB
                            </>
                        )}
                    </button>

                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            loadExampleSchema();
                        }}
                        className="px-3 py-1 text-xs bg-emerald-500/20 text-emerald-400 rounded-lg hover:bg-emerald-500/30 transition-colors"
                    >
                        Load Example
                    </button>
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
            </div>

            {/* Upload Status Notification */}
            {uploadStatus && (
                <div className={`mx-4 mt-2 p-2 rounded-lg flex items-center gap-2 text-sm ${uploadStatus.type === 'success'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-red-500/20 text-red-300 border border-red-500/30'
                    }`}>
                    {uploadStatus.type === 'success' ? (
                        <CheckCircle size={16} className="flex-shrink-0" />
                    ) : (
                        <AlertCircle size={16} className="flex-shrink-0" />
                    )}
                    <span className="flex-1">{uploadStatus.message}</span>
                    <button
                        onClick={() => setUploadStatus(null)}
                        className="text-current hover:opacity-70"
                    >
                        <X size={14} />
                    </button>
                </div>
            )}

            {/* Content */}
            {isExpanded && (
                <div className="p-3 space-y-3">
                    {/* Database Name */}
                    <div>
                        <label htmlFor="db-name" className="block text-xs text-slate-400 mb-1">Database Name</label>
                        <input
                            id="db-name"
                            name="db-name"
                            type="text"
                            value={schema.name}
                            onChange={(e) => onSchemaChange({ ...schema, name: e.target.value })}
                            className="w-full px-2 py-1.5 bg-slate-800 border border-slate-700 rounded text-slate-200 text-sm focus:outline-none focus:border-emerald-500"
                            placeholder="my_database"
                        />
                    </div>

                    {/* Tables */}
                    <div className="space-y-2">
                        {schema.tables.map((table, tableIndex) => (
                            <div
                                key={tableIndex}
                                className="border border-slate-700 rounded-lg p-2 bg-slate-800/30"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <input
                                        id={`table-${tableIndex}`}
                                        name={`table-${tableIndex}`}
                                        type="text"
                                        value={table.name}
                                        onChange={(e) => updateTable(tableIndex, "name", e.target.value)}
                                        className="flex-1 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 text-sm font-mono focus:outline-none focus:border-emerald-500"
                                        placeholder="table_name"
                                    />
                                    <button
                                        onClick={() => removeTable(tableIndex)}
                                        className="ml-2 p-1 text-slate-400 hover:text-red-400 hover:bg-red-500/20 rounded transition-colors"
                                    >
                                        <X size={16} />
                                    </button>
                                </div>

                                {/* Columns */}
                                <div className="space-y-2 mb-2">
                                    {table.columns.map((column, columnIndex) => (
                                        <div key={columnIndex} className="flex items-center gap-2 text-xs">
                                            <input
                                                id={`col-${tableIndex}-${columnIndex}`}
                                                name={`col-${tableIndex}-${columnIndex}`}
                                                type="text"
                                                value={column.name}
                                                onChange={(e) =>
                                                    updateColumn(tableIndex, columnIndex, "name", e.target.value)
                                                }
                                                className="flex-1 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 font-mono focus:outline-none"
                                                placeholder="column_name"
                                            />
                                            <select
                                                value={column.type}
                                                onChange={(e) =>
                                                    updateColumn(tableIndex, columnIndex, "type", e.target.value)
                                                }
                                                className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-slate-200 focus:outline-none"
                                            >
                                                <option>INTEGER</option>
                                                <option>TEXT</option>
                                                <option>REAL</option>
                                                <option>BOOLEAN</option>
                                                <option>DATE</option>
                                                <option>DATETIME</option>
                                            </select>
                                            <label className="flex items-center gap-1 text-slate-400">
                                                <input
                                                    type="checkbox"
                                                    checked={column.primary_key}
                                                    onChange={(e) =>
                                                        updateColumn(tableIndex, columnIndex, "primary_key", e.target.checked)
                                                    }
                                                    className="rounded"
                                                />
                                                PK
                                            </label>
                                            <button
                                                onClick={() => removeColumn(tableIndex, columnIndex)}
                                                className="p-1 text-slate-400 hover:text-red-400 rounded"
                                            >
                                                <X size={14} />
                                            </button>
                                        </div>
                                    ))}
                                </div>

                                <button
                                    onClick={() => addColumn(tableIndex)}
                                    className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                                >
                                    <Plus size={14} /> Add Column
                                </button>
                            </div>
                        ))}
                    </div>

                    {/* Add Table Button */}
                    <button
                        onClick={addTable}
                        className="w-full py-2 border-2 border-dashed border-slate-700 rounded-lg text-slate-400 hover:border-emerald-500 hover:text-emerald-400 transition-colors text-sm flex items-center justify-center gap-2"
                    >
                        <Plus size={16} />
                        Add Table
                    </button>

                    {/* Tip */}
                    <div className="flex items-start gap-2 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                        <Info size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                        <div className="text-xs text-blue-300">
                            <p className="font-semibold mb-1">💡 Quick Ways to Add Schema:</p>
                            <ul className="list-disc list-inside space-y-1">
                                <li><strong>Upload Files:</strong> SQLite (.db), Excel (.xlsx, .xls), CSV (.csv), SQL dumps (.sql), JSON (.json)</li>
                                <li><strong>Load Example:</strong> Try the pre-built music database schema</li>
                                <li><strong>Manual Entry:</strong> Use the forms above to define tables and columns</li>
                            </ul>
                            <p className="mt-2 text-blue-400">After uploading, the schema is editable - review and modify before generating queries.</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SchemaInput;
