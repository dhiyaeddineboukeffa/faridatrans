'use client';

import { useState } from 'react';

export default function AdminPage() {
    const [password, setPassword] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [formData, setFormData] = useState({
        id: '',
        name: '',
        lat: '',
        lon: '',
        type: 'bus'
    });
    const [message, setMessage] = useState('');

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        // Simple client-side check for UX, real check is on server
        if (password) setIsAuthenticated(true);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await fetch('http://localhost:8000/admin/stops', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-admin-password': password
                },
                body: JSON.stringify({
                    ...formData,
                    lat: parseFloat(formData.lat),
                    lon: parseFloat(formData.lon)
                })
            });

            if (res.ok) {
                setMessage('Stop added successfully!');
                setFormData({ id: '', name: '', lat: '', lon: '', type: 'bus' });
            } else {
                const data = await res.json();
                setMessage(`Error: ${data.detail || 'Failed to add stop'}`);
            }
        } catch (error) {
            setMessage('Network error');
        }
    };

    if (!isAuthenticated) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-100">
                <form onSubmit={handleLogin} className="bg-white p-8 rounded shadow-md">
                    <h1 className="text-2xl font-bold mb-4">Admin Login</h1>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter Admin Password"
                        className="w-full p-2 border rounded mb-4"
                    />
                    <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded">
                        Login
                    </button>
                </form>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-2xl mx-auto bg-white p-8 rounded shadow">
                <h1 className="text-2xl font-bold mb-6">Add New Stop</h1>

                {message && (
                    <div className={`p-4 mb-4 rounded ${message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                        {message}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Stop ID</label>
                        <input
                            type="text"
                            value={formData.id}
                            onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                            className="w-full p-2 border rounded"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Name</label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full p-2 border rounded"
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Latitude</label>
                            <input
                                type="number"
                                step="any"
                                value={formData.lat}
                                onChange={(e) => setFormData({ ...formData, lat: e.target.value })}
                                className="w-full p-2 border rounded"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-1">Longitude</label>
                            <input
                                type="number"
                                step="any"
                                value={formData.lon}
                                onChange={(e) => setFormData({ ...formData, lon: e.target.value })}
                                className="w-full p-2 border rounded"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">Type</label>
                        <select
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                            className="w-full p-2 border rounded"
                        >
                            <option value="bus">Bus</option>
                            <option value="tram">Tram</option>
                            <option value="taxi">Taxi</option>
                        </select>
                    </div>

                    <button type="submit" className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700">
                        Add Stop
                    </button>
                </form>
            </div>
        </div>
    );
}
