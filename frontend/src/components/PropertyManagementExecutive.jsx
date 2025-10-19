import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BuildingOfficeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  ChartBarIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  StarIcon,
  CalendarIcon,
  HomeIcon,
  BanknotesIcon,
  TrendingUpIcon,
  TrendingDownIcon
} from '@heroicons/react/24/outline';
import { 
  BuildingOfficeIcon as BuildingOfficeIconSolid,
  StarIcon as StarIconSolid
} from '@heroicons/react/24/solid';

const PropertyManagement = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [showAddProperty, setShowAddProperty] = useState(false);
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch properties from API
  useEffect(() => {
    const fetchProperties = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8001/api/properties');
        if (!response.ok) {
          throw new Error('Failed to fetch properties');
        }
        const data = await response.json();
        
        // Map API data to component format
        const mappedProperties = data.properties.map(prop => ({
          id: prop.id,
          name: prop.name,
          address: `${prop.address}, ${prop.city}, ${prop.state}`,
          type: prop.property_type || 'Commercial',
          status: prop.status || 'active',
          value: prop.current_market_value || 0,
          monthlyRent: prop.monthly_rent || 0,
          occupancy: 95, // Default if not available
          totalUnits: 1,
          occupiedUnits: 1,
          yearBuilt: prop.year_built || 2024,
          size: prop.square_footage ? `${prop.square_footage.toLocaleString()} sq ft` : 'N/A',
          rating: 4.5,
          image: '/api/placeholder/400/300',
          manager: 'Property Manager',
          lastInspection: new Date().toISOString().split('T')[0],
          nextMaintenance: new Date().toISOString().split('T')[0],
          tenants: [],
          performance: {
            rentGrowth: 0,
            maintenanceCost: 0,
            netIncome: prop.monthly_rent || 0,
            roi: 10
          }
        }));
        
        setProperties(mappedProperties);
      } catch (err) {
        console.error('Error fetching properties:', err);
        setError(err.message);
        // Fallback to empty array if fetch fails
        setProperties([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  // Mock property data (fallback/example)
  const mockProperties = [
    {
      id: 1,
      name: 'Skyline Tower',
      address: '123 Business District, Downtown',
      type: 'Commercial',
      status: 'active',
      value: 12500000,
      monthlyRent: 125000,
      occupancy: 92,
      totalUnits: 45,
      occupiedUnits: 41,
      yearBuilt: 2019,
      size: '125,000 sq ft',
      rating: 4.8,
      image: '/api/placeholder/400/300',
      manager: 'Sarah Johnson',
      lastInspection: '2024-09-15',
      nextMaintenance: '2024-10-20',
      tenants: [
        { name: 'Tech Corp Inc.', rent: 35000, lease: '3 years' },
        { name: 'Finance Solutions', rent: 28000, lease: '2 years' },
        { name: 'Marketing Agency', rent: 22000, lease: '1 year' }
      ],
      performance: {
        rentGrowth: 8.5,
        maintenanceCost: 15000,
        netIncome: 110000,
        roi: 12.3
      }
    },
    {
      id: 2,
      name: 'Garden Residences',
      address: '456 Maple Street, Suburbia',
      type: 'Residential',
      status: 'active',
      value: 8750000,
      monthlyRent: 87500,
      occupancy: 96,
      totalUnits: 120,
      occupiedUnits: 115,
      yearBuilt: 2021,
      size: '85,000 sq ft',
      rating: 4.6,
      image: '/api/placeholder/400/300',
      manager: 'Mike Chen',
      lastInspection: '2024-09-10',
      nextMaintenance: '2024-11-05',
      tenants: [
        { name: 'Various Residents', rent: 87500, lease: 'Mixed' }
      ],
      performance: {
        rentGrowth: 6.2,
        maintenanceCost: 12000,
        netIncome: 75500,
        roi: 10.8
      }
    },
    {
      id: 3,
      name: 'Industrial Park A',
      address: '789 Manufacturing Ave, Industrial Zone',
      type: 'Industrial',
      status: 'maintenance',
      value: 15000000,
      monthlyRent: 95000,
      occupancy: 75,
      totalUnits: 8,
      occupiedUnits: 6,
      yearBuilt: 2015,
      size: '200,000 sq ft',
      rating: 4.2,
      image: '/api/placeholder/400/300',
      manager: 'David Rodriguez',
      lastInspection: '2024-08-20',
      nextMaintenance: '2024-10-10',
      tenants: [
        { name: 'Manufacturing Co.', rent: 45000, lease: '5 years' },
        { name: 'Logistics Ltd.', rent: 30000, lease: '3 years' }
      ],
      performance: {
        rentGrowth: -2.1,
        maintenanceCost: 25000,
        netIncome: 70000,
        roi: 8.4
      }
    },
    {
      id: 4,
      name: 'Luxury Condos',
      address: '321 Premium Boulevard, Uptown',
      type: 'Luxury',
      status: 'active',
      value: 22000000,
      monthlyRent: 185000,
      occupancy: 88,
      totalUnits: 35,
      occupiedUnits: 31,
      yearBuilt: 2022,
      size: '95,000 sq ft',
      rating: 4.9,
      image: '/api/placeholder/400/300',
      manager: 'Emily Watson',
      lastInspection: '2024-09-25',
      nextMaintenance: '2024-12-01',
      tenants: [
        { name: 'High-end Residents', rent: 185000, lease: 'Mixed' }
      ],
      performance: {
        rentGrowth: 12.8,
        maintenanceCost: 18000,
        netIncome: 167000,
        roi: 15.2
      }
    }
  ];

  // Filter properties based on search and filter
  const filteredProperties = useMemo(() => {
    return properties.filter(property => {
      const matchesSearch = property.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          property.address.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = selectedFilter === 'all' || property.type.toLowerCase() === selectedFilter.toLowerCase();
      return matchesSearch && matchesFilter;
    });
  }, [searchTerm, selectedFilter, properties]);

  // Calculate portfolio summary
  const portfolioSummary = useMemo(() => {
    const totalValue = properties.reduce((sum, p) => sum + p.value, 0);
    const totalRent = properties.reduce((sum, p) => sum + p.monthlyRent, 0);
    const totalUnits = properties.reduce((sum, p) => sum + p.totalUnits, 0);
    const occupiedUnits = properties.reduce((sum, p) => sum + p.occupiedUnits, 0);
    const avgOccupancy = totalUnits > 0 ? (occupiedUnits / totalUnits) * 100 : 0;
    
    return {
      totalValue,
      totalRent,
      totalProperties: properties.length,
      avgOccupancy,
      totalUnits,
      occupiedUnits
    };
  }, [properties]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-emerald-600 bg-emerald-50 border-emerald-200';
      case 'maintenance': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'vacant': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'Commercial': return BuildingOfficeIcon;
      case 'Residential': return HomeIcon;
      case 'Industrial': return BuildingOfficeIcon;
      case 'Luxury': return BuildingOfficeIconSolid;
      default: return BuildingOfficeIcon;
    }
  };

  const PropertyCard = ({ property, index }) => {
    const TypeIcon = getTypeIcon(property.type);
    
    return (
      <motion.div
        key={property.id}
        variants={itemVariants}
        className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group border border-white/20"
        whileHover={{ 
          scale: 1.02,
          y: -5,
          transition: { type: "spring", stiffness: 400, damping: 25 }
        }}
      >
        {/* Property Image */}
        <div className="relative h-48 bg-gradient-to-br from-indigo-100 to-purple-100 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 to-purple-600/20" />
          <div className="absolute top-4 left-4 flex items-center space-x-2">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(property.status)}`}>
              {property.status.charAt(0).toUpperCase() + property.status.slice(1)}
            </div>
            <div className="px-3 py-1 rounded-full text-xs font-semibold bg-white/20 text-white border border-white/30">
              {property.type}
            </div>
          </div>
          
          <div className="absolute top-4 right-4 flex items-center space-x-1 bg-white/20 backdrop-blur-sm rounded-lg px-2 py-1">
            <StarIcon className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="text-white text-sm font-semibold">{property.rating}</span>
          </div>
          
          <div className="absolute inset-0 flex items-center justify-center">
            <TypeIcon className="w-16 h-16 text-white/30" />
          </div>
        </div>

        {/* Property Details */}
        <div className="p-6">
          <div className="mb-4">
            <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors duration-200">
              {property.name}
            </h3>
            <div className="flex items-center text-gray-500 text-sm">
              <MapPinIcon className="w-4 h-4 mr-1" />
              {property.address}
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center p-3 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg">
              <div className="text-2xl font-bold text-emerald-600">
                ${(property.value / 1000000).toFixed(1)}M
              </div>
              <div className="text-xs text-gray-500">Property Value</div>
            </div>
            <div className="text-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {property.occupancy}%
              </div>
              <div className="text-xs text-gray-500">Occupancy</div>
            </div>
          </div>

          {/* Monthly Performance */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-600">Monthly Rent</span>
              <div className="flex items-center space-x-1">
                {property.performance.rentGrowth > 0 ? (
                  <TrendingUpIcon className="w-4 h-4 text-emerald-500" />
                ) : (
                  <TrendingDownIcon className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm font-semibold ${
                  property.performance.rentGrowth > 0 ? 'text-emerald-600' : 'text-red-600'
                }`}>
                  {property.performance.rentGrowth > 0 ? '+' : ''}{property.performance.rentGrowth}%
                </span>
              </div>
            </div>
            <div className="text-lg font-bold text-gray-900">
              ${property.monthlyRent.toLocaleString()}
            </div>
          </div>

          {/* Units Info */}
          <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
            <div className="flex items-center space-x-1">
              <UserGroupIcon className="w-4 h-4" />
              <span>{property.occupiedUnits}/{property.totalUnits} units</span>
            </div>
            <div className="flex items-center space-x-1">
              <CalendarIcon className="w-4 h-4" />
              <span>{property.yearBuilt}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <motion.button
              onClick={() => setSelectedProperty(property)}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <EyeIcon className="w-4 h-4" />
              <span className="text-sm font-medium">View Details</span>
            </motion.button>
            <motion.button
              className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all duration-200"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <PencilIcon className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Portfolio Summary Cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 p-6 rounded-2xl text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <BanknotesIcon className="w-8 h-8 text-white/80" />
            <div className="text-right">
              <div className="text-2xl font-bold">
                ${(portfolioSummary.totalValue / 1000000).toFixed(1)}M
              </div>
              <div className="text-emerald-100 text-sm">Total Portfolio Value</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-6 rounded-2xl text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <CurrencyDollarIcon className="w-8 h-8 text-white/80" />
            <div className="text-right">
              <div className="text-2xl font-bold">
                ${(portfolioSummary.totalRent / 1000).toFixed(0)}K
              </div>
              <div className="text-blue-100 text-sm">Monthly Revenue</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-6 rounded-2xl text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <BuildingOfficeIcon className="w-8 h-8 text-white/80" />
            <div className="text-right">
              <div className="text-2xl font-bold">{portfolioSummary.totalProperties}</div>
              <div className="text-purple-100 text-sm">Properties</div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-red-600 p-6 rounded-2xl text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <UserGroupIcon className="w-8 h-8 text-white/80" />
            <div className="text-right">
              <div className="text-2xl font-bold">{portfolioSummary.avgOccupancy.toFixed(1)}%</div>
              <div className="text-orange-100 text-sm">Avg Occupancy</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Search and Filter Controls */}
      <motion.div variants={itemVariants} className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search properties..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white/50 backdrop-blur-sm"
            />
          </div>

          <div className="flex items-center space-x-2">
            <FunnelIcon className="w-5 h-5 text-gray-500" />
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white/50 backdrop-blur-sm"
            >
              <option value="all">All Types</option>
              <option value="commercial">Commercial</option>
              <option value="residential">Residential</option>
              <option value="industrial">Industrial</option>
              <option value="luxury">Luxury</option>
            </select>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <motion.button
            onClick={() => setShowAddProperty(true)}
            className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
          >
            <PlusIcon className="w-5 h-5" />
            <span className="font-medium">Add Property</span>
          </motion.button>
        </div>
      </motion.div>

      {/* Properties Grid */}
      <motion.div 
        variants={containerVariants}
        className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
      >
        {filteredProperties.map((property, index) => (
          <PropertyCard key={property.id} property={property} index={index} />
        ))}
      </motion.div>

      {/* Property Details Modal */}
      <AnimatePresence>
        {selectedProperty && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedProperty(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="bg-white rounded-2xl p-8 max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">{selectedProperty.name}</h2>
                  <p className="text-gray-600">{selectedProperty.address}</p>
                </div>
                <button
                  onClick={() => setSelectedProperty(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                >
                  <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Detailed property information would go here */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900">Property Details</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-medium">{selectedProperty.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Size:</span>
                      <span className="font-medium">{selectedProperty.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Year Built:</span>
                      <span className="font-medium">{selectedProperty.yearBuilt}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Manager:</span>
                      <span className="font-medium">{selectedProperty.manager}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900">Financial Performance</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Monthly Income:</span>
                      <span className="font-medium text-emerald-600">
                        ${selectedProperty.performance.netIncome.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">ROI:</span>
                      <span className="font-medium text-blue-600">
                        {selectedProperty.performance.roi}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Rent Growth:</span>
                      <span className={`font-medium ${
                        selectedProperty.performance.rentGrowth > 0 ? 'text-emerald-600' : 'text-red-600'
                      }`}>
                        {selectedProperty.performance.rentGrowth > 0 ? '+' : ''}{selectedProperty.performance.rentGrowth}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default PropertyManagement;