import { Sidebar } from "@/components/layout/Sidebar";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-[#0A0F1C]">
            {/* Grid Background */}
            <div className="grid-background" />

            {/* Gradient Orbs */}
            <div className="fixed top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-[#3B82F6] opacity-[0.02] blur-[120px] pointer-events-none" />
            <div className="fixed bottom-[-20%] left-[20%] w-[500px] h-[500px] rounded-full bg-[#10B981] opacity-[0.02] blur-[120px] pointer-events-none" />

            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <main className="min-h-screen relative z-10 transition-all duration-300" style={{ marginLeft: '288px' }}>
                <div className="max-w-[1920px] mx-auto w-full">
                    {children}
                </div>
            </main>
        </div>
    );
}
