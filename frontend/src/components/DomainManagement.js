import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useAuth } from '../contexts/AuthContext';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Globe, 
  Shield, 
  Settings,
  CheckCircle,
  XCircle
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const DomainManagement = () => {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingDomain, setEditingDomain] = useState(null);

  const { data: domains, isLoading } = useQuery(
    'domains',
    async () => {
      const response = await axios.get('/admin/domains', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  );

  const addDomainMutation = useMutation(
    async (domainData) => {
      const response = await axios.post('/admin/domains', domainData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('domains');
        setShowAddModal(false);
        toast.success('Domain added successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to add domain');
      }
    }
  );

  const updateDomainMutation = useMutation(
    async ({ id, data }) => {
      const response = await axios.put(`/admin/domains/${id}`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('domains');
        setEditingDomain(null);
        toast.success('Domain updated successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to update domain');
      }
    }
  );

  const deleteDomainMutation = useMutation(
    async (id) => {
      await axios.delete(`/admin/domains/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('domains');
        toast.success('Domain deleted successfully');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to delete domain');
      }
    }
  );

  const handleAddDomain = (formData) => {
    addDomainMutation.mutate(formData);
  };

  const handleUpdateDomain = (id, formData) => {
    updateDomainMutation.mutate({ id, data: formData });
  };

  const handleDeleteDomain = (id) => {
    if (window.confirm('Are you sure you want to delete this domain?')) {
      deleteDomainMutation.mutate(id);
    }
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
          <h1 className="text-2xl font-bold text-gray-900">Domain Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage protected domains and their security settings
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Domain
        </button>
      </div>

      {/* Domains List */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Protected Domains</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {domains?.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <Globe className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No domains</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by adding a new domain to protect.
              </p>
            </div>
          ) : (
            domains?.map((domain) => (
              <div key={domain.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Globe className="h-8 w-8 text-primary-600" />
                    </div>
                    <div className="ml-4">
                      <div className="flex items-center">
                        <h4 className="text-lg font-medium text-gray-900">
                          {domain.domain_name}
                        </h4>
                        {domain.is_active ? (
                          <CheckCircle className="ml-2 h-5 w-5 text-success-500" />
                        ) : (
                          <XCircle className="ml-2 h-5 w-5 text-danger-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-500">
                        Target: {domain.target_url}
                      </p>
                      <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <Shield className="h-4 w-4 mr-1" />
                          {domain.security_level}
                        </span>
                        <span className="flex items-center">
                          <Settings className="h-4 w-4 mr-1" />
                          {domain.rate_limit} req/hour
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setEditingDomain(domain)}
                      className="text-primary-600 hover:text-primary-900"
                    >
                      <Edit className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteDomain(domain.id)}
                      className="text-danger-600 hover:text-danger-900"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Domain Modal */}
      {showAddModal && (
        <DomainModal
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddDomain}
          isLoading={addDomainMutation.isLoading}
        />
      )}

      {/* Edit Domain Modal */}
      {editingDomain && (
        <DomainModal
          domain={editingDomain}
          onClose={() => setEditingDomain(null)}
          onSubmit={(data) => handleUpdateDomain(editingDomain.id, data)}
          isLoading={updateDomainMutation.isLoading}
        />
      )}
    </div>
  );
};

const DomainModal = ({ domain, onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    domain_name: domain?.domain_name || '',
    target_url: domain?.target_url || '',
    security_level: domain?.security_level || 'moderate',
    rate_limit: domain?.rate_limit || 1000,
    is_active: domain?.is_active ?? true,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />
        
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {domain ? 'Edit Domain' : 'Add New Domain'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="label">Domain Name</label>
                  <input
                    type="text"
                    name="domain_name"
                    value={formData.domain_name}
                    onChange={handleChange}
                    className="input"
                    placeholder="example.com"
                    required
                  />
                </div>
                
                <div>
                  <label className="label">Target URL</label>
                  <input
                    type="url"
                    name="target_url"
                    value={formData.target_url}
                    onChange={handleChange}
                    className="input"
                    placeholder="https://backend.example.com"
                    required
                  />
                </div>
                
                <div>
                  <label className="label">Security Level</label>
                  <select
                    name="security_level"
                    value={formData.security_level}
                    onChange={handleChange}
                    className="input"
                  >
                    <option value="relaxed">Relaxed</option>
                    <option value="moderate">Moderate</option>
                    <option value="strict">Strict</option>
                  </select>
                </div>
                
                <div>
                  <label className="label">Rate Limit (requests per hour)</label>
                  <input
                    type="number"
                    name="rate_limit"
                    value={formData.rate_limit}
                    onChange={handleChange}
                    className="input"
                    min="1"
                    max="10000"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">
                    Active
                  </label>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn btn-primary sm:ml-3 sm:w-auto disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : (domain ? 'Update' : 'Add')}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="mt-3 w-full btn btn-secondary sm:mt-0 sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DomainManagement;
