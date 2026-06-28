import { useState } from "react";
import { PageHeader } from "../../../components/layout/PageHeader";

export function SettingsPage() {
  const [settings, setSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    darkMode: false,
    autoApproveClaims: false,
    language: "English",
  });

  const [showPasswordModal, setShowPasswordModal] = useState(false);

  const [passwords, setPasswords] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleToggle = (key: keyof typeof settings) => {
    if (typeof settings[key] === "boolean") {
      setSettings((prev) => ({
        ...prev,
        [key]: !prev[key],
      }));
    }
  };

  const handlePasswordChange = () => {
    alert("Password changed successfully!");

    setPasswords({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });

    setShowPasswordModal(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        subtitle="Manage platform configuration"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Notifications */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            Notifications
          </h2>

          <div className="space-y-4">
            <label className="flex justify-between items-center">
              <span>Email Notifications</span>

              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={() => handleToggle("emailNotifications")}
              />
            </label>

            <label className="flex justify-between items-center">
              <span>SMS Notifications</span>

              <input
                type="checkbox"
                checked={settings.smsNotifications}
                onChange={() => handleToggle("smsNotifications")}
              />
            </label>
          </div>
        </div>

        {/* System */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            System
          </h2>

          <div className="space-y-4">
            <label className="flex justify-between items-center">
              <span>Dark Mode</span>

              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={() => handleToggle("darkMode")}
              />
            </label>

            <label className="flex justify-between items-center">
              <span>Auto Approve Claims</span>

              <input
                type="checkbox"
                checked={settings.autoApproveClaims}
                onChange={() => handleToggle("autoApproveClaims")}
              />
            </label>
          </div>
        </div>

        {/* Language */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            Language
          </h2>

          <select
            value={settings.language}
            onChange={(e) =>
              setSettings({
                ...settings,
                language: e.target.value,
              })
            }
            className="border rounded-lg px-3 py-2 w-full"
          >
            <option>English</option>
            <option>Hindi</option>
          </select>
        </div>

        {/* Security */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">
            Security
          </h2>

          <button
            onClick={() => setShowPasswordModal(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
          >
            Change Password
          </button>
        </div>
      </div>

      {/* Password Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">

            <h2 className="text-2xl font-bold mb-5">
              Change Password
            </h2>

            <div className="space-y-4">

              <input
                type="password"
                placeholder="Current Password"
                value={passwords.currentPassword}
                onChange={(e) =>
                  setPasswords({
                    ...passwords,
                    currentPassword: e.target.value,
                  })
                }
                className="w-full border rounded-lg px-3 py-2"
              />

              <input
                type="password"
                placeholder="New Password"
                value={passwords.newPassword}
                onChange={(e) =>
                  setPasswords({
                    ...passwords,
                    newPassword: e.target.value,
                  })
                }
                className="w-full border rounded-lg px-3 py-2"
              />

              <input
                type="password"
                placeholder="Confirm Password"
                value={passwords.confirmPassword}
                onChange={(e) =>
                  setPasswords({
                    ...passwords,
                    confirmPassword: e.target.value,
                  })
                }
                className="w-full border rounded-lg px-3 py-2"
              />

            </div>

            <div className="flex justify-end gap-3 mt-6">

              <button
                onClick={() => setShowPasswordModal(false)}
                className="px-4 py-2 rounded-lg border"
              >
                Cancel
              </button>

              <button
                onClick={handlePasswordChange}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg"
              >
                Save
              </button>

            </div>

          </div>

        </div>
      )}
    </div>
  );
}