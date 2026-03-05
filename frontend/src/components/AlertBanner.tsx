export default function AlertBanner({ message }: { message: string }) {
  return (
    <div className="bg-red-50 border border-red-500 rounded-lg px-5 py-4 flex items-start gap-3 mb-6">
      <span className="text-lg shrink-0">🔴</span>
      <div>
        <p className="font-medium text-red-800">CASO COMPLEXO</p>
        <p className="text-red-700 text-sm mt-1">{message}</p>
      </div>
    </div>
  );
}
