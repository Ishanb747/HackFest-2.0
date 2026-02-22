import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import './DataTable.css';

function DataTable({ 
  columns, 
  data, 
  onRowClick,
  selectedRows = [],
  onSelectRow,
  showCheckbox = false,
  emptyMessage = 'No data available',
  pagination,
  onPageChange
}) {
  const allSelected = data.length > 0 && selectedRows.length === data.length;

  const handleSelectAll = () => {
    if (allSelected) {
      onSelectRow && onSelectRow([]);
    } else {
      onSelectRow && onSelectRow(data.map((_, i) => i));
    }
  };

  const handleSelectRow = (index) => {
    if (selectedRows.includes(index)) {
      onSelectRow && onSelectRow(selectedRows.filter(i => i !== index));
    } else {
      onSelectRow && onSelectRow([...selectedRows, index]);
    }
  };

  return (
    <div className="data-table-wrapper">
      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              {showCheckbox && (
                <th className="checkbox-cell">
                  <input 
                    type="checkbox" 
                    checked={allSelected}
                    onChange={handleSelectAll}
                    className="table-checkbox"
                  />
                </th>
              )}
              <th className="index-cell">#</th>
              {columns.map((col, index) => (
                <th 
                  key={index}
                  className={col.align ? `align-${col.align}` : ''}
                  style={{ width: col.width }}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr>
                <td 
                  colSpan={columns.length + (showCheckbox ? 2 : 1)} 
                  className="empty-cell"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, rowIndex) => (
                <tr 
                  key={rowIndex}
                  className={`${onRowClick ? 'clickable' : ''} ${selectedRows.includes(rowIndex) ? 'selected' : ''}`}
                  onClick={() => onRowClick && onRowClick(row, rowIndex)}
                >
                  {showCheckbox && (
                    <td className="checkbox-cell" onClick={(e) => e.stopPropagation()}>
                      <input 
                        type="checkbox" 
                        checked={selectedRows.includes(rowIndex)}
                        onChange={() => handleSelectRow(rowIndex)}
                        className="table-checkbox"
                      />
                    </td>
                  )}
                  <td className="index-cell">{rowIndex + 1}</td>
                  {columns.map((col, colIndex) => (
                    <td 
                      key={colIndex}
                      className={col.align ? `align-${col.align}` : ''}
                    >
                      {col.render ? col.render(row[col.accessor], row) : row[col.accessor]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {pagination && (
        <div className="table-pagination">
          <span className="pagination-info">
            {pagination.from}-{pagination.to} of {pagination.total} records
          </span>
          <div className="pagination-controls">
            <button 
              className="pagination-btn"
              disabled={pagination.currentPage === 1}
              onClick={() => onPageChange && onPageChange(pagination.currentPage - 1)}
            >
              <ChevronLeft size={18} />
            </button>
            <span className="pagination-pages">
              Page {pagination.currentPage} of {pagination.totalPages}
            </span>
            <button 
              className="pagination-btn"
              disabled={pagination.currentPage === pagination.totalPages}
              onClick={() => onPageChange && onPageChange(pagination.currentPage + 1)}
            >
              <ChevronRight size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataTable;
