import React from 'react';
import { useQuery } from 'react-query';
import { 
  Shield, 
  Globe, 
  AlertTriangle, 
  CheckCircle, 
  Activity,
  TrendingUp,
  Clock
} from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
  const { data: stats, isLoading, error } = useQuery(
    'dashboard-stats',
    async () => {
      const response = await axios.get('/admin/stats');
      return response.data;
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-danger-50 border border-danger-200 rounded-md p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-danger-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-danger-800">
              Error loading dashboard
            </h3>
            <div className="mt-2 text-sm text-danger-700">
              {error.message}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      name: 'Total Domains',
      value: stats?.total_domains || 0,
      icon: Globe,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Active Domains',
      value: stats?.active_domains || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'Total Requests',
      value: stats?.total_requests || 0,
      icon: Activity,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      name: 'Blocked Requests',
      value: stats?.blocked_requests || 0,
      icon: Shield,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Recent Attacks (24h)',
      value: stats?.recent_attacks || 0,
      icon: AlertTriangle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  const blockRate = stats?.total_requests > 0 
    ? ((stats.blocked_requests / stats.total_requests) * 100).toFixed(2)
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of your Web Application Firewall
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-5">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card p-6">
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${stat.bgColor} rounded-md p-3`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stat.value.toLocaleString()}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Block Rate */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Block Rate</h3>
            <p className="text-sm text-gray-500">Percentage of requests blocked</p>
          </div>
          <div className="text-3xl font-bold text-gray-900">
            {blockRate}%
          </div>
        </div>
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(blockRate, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Top Attack Types */}
      {stats?.top_attack_types && stats.top_attack_types.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Attack Types</h3>
          <div className="space-y-3">
            {stats.top_attack_types.map((attack, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className="h-5 w-5 text-danger-500" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">
                      {attack.type}
                    </p>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  {attack.count} attacks
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Status */}
      <div className="card p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <CheckCircle className="h-8 w-8 text-success-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
            <p className="text-sm text-gray-500">
              WAF is running and protecting your domains
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
