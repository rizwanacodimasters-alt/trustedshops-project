import React, { useState, useEffect } from 'react';
import { securityAPI } from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Activity,
  Globe,
  TrendingUp,
  Clock
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

const SecurityMonitoring = () => {
  const [statistics, setStatistics] = useState(null);
  const [loginLogs, setLoginLogs] = useState([]);
  const [failedLogins, setFailedLogins] = useState([]);
  const [suspiciousActivities, setSuspiciousActivities] = useState([]);
  const [ipTracking, setIpTracking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);
  const { toast } = useToast();

  useEffect(() => {
    fetchAllData();
  }, [days]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchStatistics(),
        fetchLoginLogs(),
        fetchFailedLogins(),
        fetchSuspiciousActivities(),
        fetchIpTracking()
      ]);
    } catch (error) {
      console.error('Error fetching security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await securityAPI.getStatistics({ days });
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const fetchLoginLogs = async () => {
    try {
      const response = await securityAPI.getLoginLogs({ days, limit: 50 });
      setLoginLogs(response.data.data || []);
    } catch (error) {
      console.error('Error fetching login logs:', error);
      setLoginLogs([]);
    }
  };

  const fetchFailedLogins = async () => {
    try {
      const response = await securityAPI.getFailedLogins({ days, limit: 50 });
      setFailedLogins(response.data.data || []);
    } catch (error) {
      console.error('Error fetching failed logins:', error);
      setFailedLogins([]);
    }
  };

  const fetchSuspiciousActivities = async () => {
    try {
      const response = await securityAPI.getSuspiciousActivities({ limit: 50 });
      setSuspiciousActivities(response.data.data || []);
    } catch (error) {
      console.error('Error fetching suspicious activities:', error);
      setSuspiciousActivities([]);
    }
  };

  const fetchIpTracking = async () => {
    try {
      const response = await securityAPI.getIpTracking({ days });
      setIpTracking(response.data.data || []);
    } catch (error) {
      console.error('Error fetching IP tracking:', error);
      setIpTracking([]);
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await securityAPI.resolveAlert(alertId);
      toast({
        title: 'Success',
        description: 'Alert marked as resolved',
      });
      fetchSuspiciousActivities();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to resolve alert',
        variant: 'destructive',
      });
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('de-DE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRiskBadge = (score) => {
    if (score >= 70) {
      return <Badge className="bg-red-100 text-red-800 border-red-200">High Risk ({score})</Badge>;
    } else if (score >= 40) {
      return <Badge className="bg-orange-100 text-orange-800 border-orange-200">Medium Risk ({score})</Badge>;
    } else {
      return <Badge className="bg-green-100 text-green-800 border-green-200">Low Risk ({score})</Badge>;
    }
  };

  if (loading && !statistics) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-600">Loading security data...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      {statistics && (
        <div className="grid md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Logins</p>
                  <p className="text-2xl font-bold">{statistics.total_logins}</p>
                  <p className="text-xs text-gray-500">Last {days} days</p>
                </div>
                <Activity className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-green-600">{statistics.success_rate}%</p>
                  <p className="text-xs text-gray-500">{statistics.successful_logins} successful</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Failed Logins</p>
                  <p className="text-2xl font-bold text-red-600">{statistics.failed_logins}</p>
                  <p className="text-xs text-gray-500">Last {days} days</p>
                </div>
                <XCircle className="w-8 h-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Unique IPs</p>
                  <p className="text-2xl font-bold">{statistics.unique_ips}</p>
                  <p className="text-xs text-gray-500">Active IP addresses</p>
                </div>
                <Globe className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Time Filter */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Time Range:</span>
            <div className="flex gap-2">
              {[7, 14, 30].map((d) => (
                <Button
                  key={d}
                  size="sm"
                  variant={days === d ? "default" : "outline"}
                  onClick={() => setDays(d)}
                >
                  {d} Days
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="login-logs" className="space-y-6">
        <TabsList className="bg-white p-1 rounded-lg shadow">
          <TabsTrigger value="login-logs">Login Logs</TabsTrigger>
          <TabsTrigger value="failed-logins">Failed Logins</TabsTrigger>
          <TabsTrigger value="suspicious">Suspicious Activities</TabsTrigger>
          <TabsTrigger value="ip-tracking">IP Tracking</TabsTrigger>
        </TabsList>

        {/* Login Logs Tab */}
        <TabsContent value="login-logs">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Login History
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loginLogs.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No login logs found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3">Timestamp</th>
                        <th className="text-left p-3">User</th>
                        <th className="text-left p-3">Email</th>
                        <th className="text-left p-3">IP Address</th>
                        <th className="text-left p-3">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loginLogs.map((log) => (
                        <tr key={log.id} className="border-b hover:bg-gray-50">
                          <td className="p-3 text-sm">{formatDate(log.timestamp)}</td>
                          <td className="p-3">
                            <div>
                              <p className="font-medium">{log.user_name}</p>
                              <p className="text-xs text-gray-500">{log.user_role}</p>
                            </div>
                          </td>
                          <td className="p-3 text-sm">{log.user_email}</td>
                          <td className="p-3 text-sm font-mono">{log.ip_address || 'N/A'}</td>
                          <td className="p-3">
                            {log.success ? (
                              <Badge className="bg-green-100 text-green-800">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Success
                              </Badge>
                            ) : (
                              <Badge className="bg-red-100 text-red-800">
                                <XCircle className="w-3 h-3 mr-1" />
                                Failed
                              </Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Failed Logins Tab */}
        <TabsContent value="failed-logins">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <XCircle className="w-5 h-5 text-red-500" />
                Failed Login Attempts
              </CardTitle>
            </CardHeader>
            <CardContent>
              {failedLogins.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Failed Logins</h3>
                  <p className="text-gray-600">Great! No failed login attempts in the last {days} days.</p>
                </div>
              ) : (
                <>
                  <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-200">
                    <p className="text-sm text-red-800">
                      <strong>{failedLogins.length}</strong> failed login attempts detected in the last {days} days
                    </p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-3">Timestamp</th>
                          <th className="text-left p-3">Email Attempted</th>
                          <th className="text-left p-3">IP Address</th>
                          <th className="text-left p-3">Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {failedLogins.map((log) => (
                          <tr key={log.id} className="border-b hover:bg-gray-50">
                            <td className="p-3 text-sm">{formatDate(log.timestamp)}</td>
                            <td className="p-3 text-sm font-medium">{log.email || 'N/A'}</td>
                            <td className="p-3 text-sm font-mono">{log.ip_address || 'N/A'}</td>
                            <td className="p-3 text-sm text-red-600">{log.failure_reason || 'Invalid credentials'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Suspicious Activities Tab */}
        <TabsContent value="suspicious">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                Suspicious Activities
              </CardTitle>
            </CardHeader>
            <CardContent>
              {suspiciousActivities.length === 0 ? (
                <div className="text-center py-12">
                  <Shield className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">All Clear</h3>
                  <p className="text-gray-600">No suspicious activities detected.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {suspiciousActivities.map((activity) => (
                    <div key={activity.id} className="p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-orange-500" />
                            <h4 className="font-semibold">{activity.alert_type || 'Security Alert'}</h4>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{activity.description || 'Suspicious activity detected'}</p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>User: {activity.user_name || activity.user_email || 'Unknown'}</span>
                            <span>Time: {formatDate(activity.created_at)}</span>
                            {activity.ip_address && <span>IP: {activity.ip_address}</span>}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleResolveAlert(activity.id)}
                        >
                          Resolve
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* IP Tracking Tab */}
        <TabsContent value="ip-tracking">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                IP Address Tracking
              </CardTitle>
            </CardHeader>
            <CardContent>
              {ipTracking.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No IP tracking data available</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3">IP Address</th>
                        <th className="text-left p-3">Total Attempts</th>
                        <th className="text-left p-3">Successful</th>
                        <th className="text-left p-3">Failed</th>
                        <th className="text-left p-3">Unique Users</th>
                        <th className="text-left p-3">Risk Score</th>
                        <th className="text-left p-3">Last Seen</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ipTracking.map((ip, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                          <td className="p-3 text-sm font-mono">{ip.ip_address}</td>
                          <td className="p-3 text-sm">{ip.total_attempts}</td>
                          <td className="p-3 text-sm text-green-600">{ip.successful_logins}</td>
                          <td className="p-3 text-sm text-red-600">{ip.failed_logins}</td>
                          <td className="p-3 text-sm">{ip.unique_users}</td>
                          <td className="p-3">{getRiskBadge(ip.risk_score)}</td>
                          <td className="p-3 text-sm">{formatDate(ip.last_seen)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SecurityMonitoring;
