import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";
import { GripVertical, Trash2, Plus } from "lucide-react";

interface Widget {
  id: number;
  name: string;
  description: string;
  widget_type: string;
  icon: string;
  requires_premium: boolean;
}

interface UserWidget {
  id: number;
  widget_id: number;
  widget_name: string;
  widget_type: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  is_enabled: boolean;
}

export default function CustomizeDashboard() {
  const [availableWidgets, setAvailableWidgets] = useState<Widget[]>([]);
  const [userWidgets, setUserWidgets] = useState<UserWidget[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWidgets();
    fetchUserWidgets();
  }, []);

  const fetchWidgets = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/dashboard/widgets/available`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setAvailableWidgets(data.widgets || []);
      }
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch widgets:", error);
      setLoading(false);
    }
  };

  const fetchUserWidgets = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/dashboard/layout`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setUserWidgets(data.widgets || []);
      }
    } catch (error) {
      console.error("Failed to fetch user widgets:", error);
    }
  };

  const addWidget = async (widgetId: number) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/dashboard/widgets/add`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ widget_id: widgetId })
        }
      );
      if (response.ok) {
        await fetchUserWidgets();
      }
    } catch (error) {
      console.error("Failed to add widget:", error);
    }
  };

  const removeWidget = async (userWidgetId: number) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/dashboard/widgets/${userWidgetId}`,
        { method: "DELETE", credentials: "include" }
      );
      if (response.ok) {
        await fetchUserWidgets();
      }
    } catch (error) {
      console.error("Failed to remove widget:", error);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading widgets...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const addedWidgetIds = userWidgets.map(w => w.widget_id);

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="mb-12">
            <SectionHeading className="text-white mb-4">Customize Your Dashboard</SectionHeading>
            <p className="text-slate-300 text-lg">
              Add or remove widgets to personalize your dashboard and track what matters most to you.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Your Widgets */}
            <div className="lg:col-span-2">
              <h2 className="text-2xl font-bold text-white mb-6">Your Widgets</h2>
              {userWidgets.length > 0 ? (
                <div className="space-y-3">
                  {userWidgets.map(widget => (
                    <Card key={widget.id} className="bg-slate-800 border-slate-700 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <GripVertical className="w-5 h-5 text-slate-500 cursor-grab" />
                        <div>
                          <h3 className="font-semibold text-white">{widget.widget_name}</h3>
                          <p className="text-xs text-slate-400 capitalize">{widget.widget_type.replace(/_/g, " ")}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeWidget(widget.id)}
                        className="p-2 text-red-400 hover:bg-red-900/20 rounded-lg transition"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="bg-slate-800 border-slate-700 text-center py-8">
                  <p className="text-slate-400 mb-4">No widgets added yet</p>
                  <p className="text-slate-500 text-sm">Browse available widgets on the right to get started</p>
                </Card>
              )}
            </div>

            {/* Available Widgets */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Available Widgets</h2>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {availableWidgets.map(widget => {
                  const isAdded = addedWidgetIds.includes(widget.id);
                  return (
                    <Card
                      key={widget.id}
                      className={`${isAdded ? "bg-slate-700/50 border-slate-600" : "bg-slate-800 border-slate-700"} p-4`}
                    >
                      <div className="mb-3">
                        <div className="text-2xl mb-2">{widget.icon}</div>
                        <h3 className="font-semibold text-white text-sm mb-1">{widget.name}</h3>
                        <p className="text-xs text-slate-400 line-clamp-2">{widget.description}</p>
                      </div>
                      {widget.requires_premium && (
                        <p className="text-xs text-yellow-400 mb-3">✨ Premium only</p>
                      )}
                      <button
                        onClick={() => addWidget(widget.id)}
                        disabled={isAdded}
                        className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition ${
                          isAdded
                            ? "bg-slate-600 text-slate-400 cursor-not-allowed"
                            : "bg-blue-600 text-white hover:bg-blue-700"
                        }`}
                      >
                        {isAdded ? "Added" : "Add Widget"}
                      </button>
                    </Card>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
