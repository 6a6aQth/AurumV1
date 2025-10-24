import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { useAuth } from '../contexts/AuthContext';
import { 
  FileText, 
  Download, 
  Search, 
  Filter,
  AlertTriangle,
  Clock,
  Globe
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const SecurityLogs = () => {
  const { token } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterReason, setFilterReason] = useState('');

  const { data: logs, isLoading, refetch } = useQuery(
    ['security-logs', searchTerm, filterReason],
    async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (filterReason) params.append('reason', filterReason);
      
      const response = await axios.get(`/admin/logs?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  );

  const handleExport = async () => {
    try {
      const response = await axios.get('/admin/logs/export', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Create and download CSV file
      const blob = new Blob([response.data.csv_data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'security_logs.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Logs exported successfully');
    } catch (error) {
      toast.error('Failed to export logs');
    }
  };

  const getReasonColor = (reason) => {
    switch (reason.toLowerCase()) {
      case 'sql injection':
        return 'text-red-600 bg-red-100';
      case 'xss attack':
        return 'text-orange-600 bg-orange-100';
      case 'command injection':
        return 'text-purple-600 bg-purple-100';
      case 'path traversal':
        return 'text-blue-600 bg-blue-100';
      case 'suspicious header':
        return 'text-yellow-600 bg-yellow-100';
      case 'blocked file extension':
        return 'text-indigo-600 bg-indigo-100';
      case 'malformed request':
        return 'text-pink-600 bg-pink-100';
      case 'suspicious user agent':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Security Logs</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor and analyze security events and blocked requests
          </p>
        </div>
        <button
          onClick={handleExport}
          className="btn btn-secondary flex items-center"
        >
          <Download className="h-4 w-4 mr-2" />
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="label">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
                placeholder="Search by IP, path, or method..."
              />
            </div>
          </div>
          <div>
            <label className="label">Filter by Reason</label>
            <select
              value={filterReason}
              onChange={(e) => setFilterReason(e.target.value)}
              className="input"
            >
              <option value="">All reasons</option>
              <option value="SQL Injection">SQL Injection</option>
              <option value="XSS Attack">XSS Attack</option>
              <option value="Command Injection">Command Injection</option>
              <option value="Path Traversal">Path Traversal</option>
              <option value="Suspicious Header">Suspicious Header</option>
              <option value="Blocked File Extension">Blocked File Extension</option>
              <option value="Malformed Request">Malformed Request</option>
              <option value="Suspicious User Agent">Suspicious User Agent</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Security Events</h3>
        </div>
        
        {logs?.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No logs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No security events match your current filters.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Method
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Path
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reason
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User Agent
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs?.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        {formatTimestamp(log.timestamp)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <Globe className="h-4 w-4 text-gray-400 mr-2" />
                        {log.client_ip}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {log.request_method}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                      {log.request_path}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getReasonColor(log.reason)}`}>
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        {log.reason}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {log.user_agent || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={() => refetch()}
          className="btn btn-secondary"
        >
          Refresh Logs
        </button>
      </div>
    </div>
  );
};

export default SecurityLogs;
