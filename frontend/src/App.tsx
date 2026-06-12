import React, { useState, useEffect } from 'react';
import cloudArch from './assets/cloud.png';
import systemArch from './assets/system.png';

// --- Minimal Icons ---
const ShieldIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
);

const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
);

const MenuIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
);

const XIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
);

// --- Static Data ---
const VPC_RAW_SAMPLE = [
  `{"version": "version", "account_id": "account-id", "interface_id": "interface-id", "srcaddr": "srcaddr", "dstaddr": "dstaddr", "srcport": "srcport", "dstport": "dstport", "protocol": "protocol", "packets": "packets", "bytes": "bytes", "start": "start", "end": "end", "action": "action", "log_status": "log-status"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "205.210.31.185", "srcport": "3917", "dstport": "52026", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "188.166.21.241", "dstaddr": "172.31.5.247", "srcport": "47170", "dstport": "80", "protocol": "6", "packets": "6", "bytes": "969", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "79.124.62.134", "dstaddr": "172.31.5.247", "srcport": "45462", "dstport": "25912", "protocol": "6", "packets": "2", "bytes": "80", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "205.210.31.185", "dstaddr": "172.31.5.247", "srcport": "52026", "dstport": "3917", "protocol": "6", "packets": "1", "bytes": "44", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "188.166.21.241", "dstaddr": "172.31.5.247", "srcport": "47164", "dstport": "80", "protocol": "6", "packets": "6", "bytes": "926", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "203.193.179.29", "dstaddr": "172.31.5.247", "srcport": "123", "dstport": "53015", "protocol": "17", "packets": "1", "bytes": "76", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "188.166.21.241", "srcport": "80", "dstport": "47164", "protocol": "6", "packets": "4", "bytes": "600", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "24.199.88.4", "srcport": "23", "dstport": "22740", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.236.180.15", "dstaddr": "172.31.5.247", "srcport": "123", "dstport": "41936", "protocol": "17", "packets": "1", "bytes": "76", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "24.199.88.4", "dstaddr": "172.31.5.247", "srcport": "22740", "dstport": "23", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "5.61.209.224", "dstaddr": "172.31.5.247", "srcport": "40000", "dstport": "5860", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "172.236.180.15", "srcport": "41936", "dstport": "123", "protocol": "17", "packets": "1", "bytes": "76", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "5.61.209.224", "srcport": "5860", "dstport": "40000", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "188.166.21.241", "srcport": "80", "dstport": "47170", "protocol": "6", "packets": "4", "bytes": "611", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "79.124.62.134", "srcport": "25912", "dstport": "45462", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "203.193.179.29", "srcport": "53015", "dstport": "123", "protocol": "17", "packets": "1", "bytes": "76", "start": "1779950457", "end": "1779950483", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "20.12.240.188", "srcport": "80", "dstport": "44974", "protocol": "6", "packets": "4", "bytes": "600", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "107.150.100.136", "srcport": "18280", "dstport": "41729", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "78.128.112.6", "dstaddr": "172.31.5.247", "srcport": "52541", "dstport": "33506", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "195.178.110.188", "dstaddr": "172.31.5.247", "srcport": "48782", "dstport": "8022", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "35.169.206.177", "srcport": "8888", "dstport": "61234", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "109.123.101.63", "srcport": "80", "dstport": "59526", "protocol": "6", "packets": "6", "bytes": "360", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "195.178.110.188", "srcport": "8022", "dstport": "48782", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "20.12.240.188", "dstaddr": "172.31.5.247", "srcport": "44974", "dstport": "80", "protocol": "6", "packets": "6", "bytes": "430", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "109.123.101.63", "dstaddr": "172.31.5.247", "srcport": "59526", "dstport": "80", "protocol": "6", "packets": "1", "bytes": "60", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "35.169.206.177", "dstaddr": "172.31.5.247", "srcport": "61234", "dstport": "8888", "protocol": "6", "packets": "1", "bytes": "52", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "107.150.100.136", "dstaddr": "172.31.5.247", "srcport": "41729", "dstport": "18280", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "78.128.112.6", "srcport": "33506", "dstport": "52541", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950487", "end": "1779950515", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "74.82.47.23", "dstaddr": "172.31.5.247", "srcport": "40429", "dstport": "1000", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "35.203.210.45", "dstaddr": "172.31.5.247", "srcport": "52344", "dstport": "9399", "protocol": "6", "packets": "1", "bytes": "44", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "78.128.114.22", "srcport": "25744", "dstport": "54658", "protocol": "6", "packets": "4", "bytes": "160", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "204.76.203.15", "srcport": "0", "dstport": "0", "protocol": "1", "packets": "1", "bytes": "74", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "46.151.178.13", "dstaddr": "172.31.5.247", "srcport": "55264", "dstport": "17000", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "103.150.30.30", "dstaddr": "172.31.5.247", "srcport": "47548", "dstport": "22", "protocol": "6", "packets": "3", "bytes": "180", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "138.226.239.11", "srcport": "2223", "dstport": "58486", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "139.144.239.98", "srcport": "1177", "dstport": "58922", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "18.61.120.121", "srcport": "54798", "dstport": "443", "protocol": "6", "packets": "18", "bytes": "5322", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "103.150.30.30", "srcport": "22", "dstport": "47548", "protocol": "6", "packets": "6", "bytes": "360", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "139.144.239.98", "dstaddr": "172.31.5.247", "srcport": "58922", "dstport": "1177", "protocol": "6", "packets": "1", "bytes": "44", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "78.128.114.22", "dstaddr": "172.31.5.247", "srcport": "54658", "dstport": "25744", "protocol": "6", "packets": "4", "bytes": "160", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "74.82.47.23", "srcport": "1000", "dstport": "40429", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "46.151.178.13", "srcport": "17000", "dstport": "55264", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "18.61.120.121", "dstaddr": "172.31.5.247", "srcport": "443", "dstport": "54798", "protocol": "6", "packets": "22", "bytes": "6407", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "35.203.210.45", "srcport": "9399", "dstport": "52344", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "138.226.239.11", "dstaddr": "172.31.5.247", "srcport": "58486", "dstport": "2223", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "146.88.241.132", "srcport": "0", "dstport": "0", "protocol": "1", "packets": "1", "bytes": "65", "start": "1779950517", "end": "1779950546", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "139.59.74.51", "srcport": "22", "dstport": "37754", "protocol": "6", "packets": "8", "bytes": "480", "start": "1779950548", "end": "1779950568", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "34.92.33.224", "srcport": "23", "dstport": "46387", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950548", "end": "1779950568", "action": "ACCEPT", "log_status": "OK"}`,
  `{"version": "2", "account_id": "537566695708", "interface_id": "eni-09b775dd0292a9a6e", "srcaddr": "172.31.5.247", "dstaddr": "77.91.71.11", "srcport": "40919", "dstport": "58481", "protocol": "6", "packets": "1", "bytes": "40", "start": "1779950548", "end": "1779950568", "action": "ACCEPT", "log_status": "OK"}`,
];

// --- Shared Dataset Component ---
const DatasetList = ({ data, title, subtitle, maxHeight = "300px" }: { data: any[], title: string, subtitle?: string, maxHeight?: string }) => (
  <div className="border border-zinc-900 bg-black p-4 md:p-6 space-y-4">
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-zinc-900 pb-4">
      <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">{title}</h3>
      {subtitle && <span className="text-[10px] text-zinc-600 font-mono">{subtitle}</span>}
    </div>
    <div 
      style={{ maxHeight }} 
      className="overflow-auto text-[11px] font-mono space-y-1 text-zinc-400 leading-tight no-scrollbar"
    >
      {data.length > 0 ? data.map((item, i) => (
        <div key={i} className="whitespace-pre min-w-max border-b border-zinc-950 pb-1 last:border-0">
          {typeof item === 'string' ? item : JSON.stringify(item)}
        </div>
      )) : (
        <div className="text-zinc-800">NO DATA AVAILABLE.</div>
      )}
    </div>
  </div>
);

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [rawFiles, setRawFiles] = useState<string[]>([]);
  const [selectedRawFile, setSelectedRawFile] = useState<string | null>(null);
  const [rawPreview, setRawPreview] = useState<string>('');
  const [finalEvents, setFinalEvents] = useState<any[]>([]);

  useEffect(() => {
    if (currentPage === 'dashboard' || currentPage === 'final') fetchFinalEvents();
    if (currentPage === 'raw') fetchRawFiles();
    setIsMenuOpen(false);
  }, [currentPage]);

  const fetchRawFiles = async () => {
    try {
      const res = await fetch('/api/raw-logs');
      if (!res.ok) return;
      const data = await res.json();
      setRawFiles(data.files || []);
    } catch (err) { console.error(err); }
  };

  const fetchRawPreview = async (filename: string) => {
    setLoading(true);
    setSelectedRawFile(filename);
    try {
      const res = await fetch(`/api/raw-logs/${filename}`);
      if (!res.ok) throw new Error('Failed to fetch preview');
      const data = await res.json();
      setRawPreview(data.content || '');
    } catch (err) { 
      setRawPreview('ERROR_LOADING_PREVIEW');
    }
    setLoading(false);
  };

  const fetchFinalEvents = async () => {
    try {
      const res = await fetch('/api/events');
      if (!res.ok) throw new Error('Failed to fetch events');
      const data = await res.json();
      setFinalEvents(data.events || []);
    } catch (err) { console.error(err); }
  };

  const handleInvestigate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert('Investigation failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-zinc-200 font-mono text-sm selection:bg-white selection:text-black">
      {/* Navigation */}
      <nav className="border-b border-zinc-900 bg-black sticky top-0 z-50">
        <div className="container mx-auto px-4 md:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentPage('dashboard')}>
            <ShieldIcon />
            <span className="font-bold tracking-tighter uppercase text-white">ThreatLens</span>
          </div>
          
          <div className="hidden md:flex items-center gap-6 text-[10px] font-bold uppercase tracking-widest text-zinc-500">
            {['dashboard', 'raw', 'final', 'architecture', 'about'].map(p => (
              <button 
                key={p} 
                onClick={() => setCurrentPage(p)}
                className={`transition-colors whitespace-nowrap ${currentPage === p ? 'text-white border-b border-white' : 'hover:text-zinc-300'}`}
              >
                {p}
              </button>
            ))}
          </div>

          <button 
            className="md:hidden p-2 text-zinc-400 hover:text-white transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <XIcon /> : <MenuIcon />}
          </button>
        </div>

        {isMenuOpen && (
          <div className="md:hidden border-t border-zinc-900 bg-black animate-in fade-in slide-in-from-top-4 duration-300 ease-out">
            <div className="flex flex-col p-4 space-y-4 text-[10px] font-bold uppercase tracking-widest">
              {['dashboard', 'raw', 'final', 'architecture', 'about'].map(p => (
                <button 
                  key={p} 
                  onClick={() => setCurrentPage(p)}
                  className={`text-left py-3 px-4 rounded-sm transition-all duration-200 ${currentPage === p ? 'bg-zinc-100 text-black' : 'text-zinc-500 hover:text-zinc-300 active:scale-[0.98]'}`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      <main className="container mx-auto px-4 md:px-6 py-8 animate-in fade-in slide-in-from-bottom-2 duration-700 ease-in-out">
        {currentPage === 'dashboard' && (
          <div className="max-w-4xl mx-auto space-y-10">
            <header className="space-y-2">
              <h1 className="text-2xl md:text-3xl font-bold tracking-tighter text-white uppercase">AI SOC ANALYST</h1>
              <p className="text-zinc-500 text-xs leading-relaxed max-w-lg">
                VPC Flow Log analysis engine. Real data captured from my own VPC (infrastructure de-provisioned for security).
              </p>
            </header>

            {/* Dataset Preview */}
            <DatasetList 
              data={VPC_RAW_SAMPLE}
              title="CAPTURED_VPC_DATA_PREVIEW"
              maxHeight="220px"
            />

            {/* Search */}
            <form onSubmit={handleInvestigate} className="space-y-4">
              <div className="relative">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-zinc-600">
                  <SearchIcon />
                </div>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Query (e.g. ssh attacks)"
                  className="w-full bg-black border border-zinc-800 text-white py-4 pl-12 pr-4 focus:outline-none focus:border-zinc-500 transition-all text-sm placeholder:text-zinc-800"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-zinc-100 text-black font-bold text-xs uppercase tracking-widest hover:bg-white active:scale-[0.99] disabled:bg-zinc-800 disabled:text-zinc-500 transition-all duration-300 ease-in-out"
              >
                {loading ? '...SCANNING...' : 'EXECUTE_SCAN'}
              </button>

              {/* FAQ Buttons */}
              <div className="flex flex-wrap gap-2 pt-2">
                {[
                  "Show high severity SSH attacks",
                  "What happened at 12:00?",
                  "Find suspicious port scanning",
                  "Show rejected network traffic"
                ].map((faq) => (
                  <button
                    key={faq}
                    onClick={() => setQuery(faq)}
                    className="text-[10px] font-bold uppercase tracking-widest px-4 py-2 bg-zinc-950 border border-zinc-900 text-zinc-600 hover:text-white hover:border-white transition-all active:scale-[0.97]"
                  >
                    {faq}
                  </button>
                ))}
              </div>
            </form>

            {/* Result Area */}
            {result && (
              <div className="space-y-6 pt-10 border-t border-zinc-900 animate-in fade-in slide-in-from-bottom-6 duration-1000 ease-out">
                <div className="space-y-2">
                  <h3 className="text-[10px] font-bold uppercase text-zinc-500">ANALYSIS_REPORT</h3>
                  <div className="text-zinc-300 leading-relaxed text-xs whitespace-pre-wrap font-sans bg-zinc-950 p-4 border border-zinc-900">
                    {result.analysis}
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="text-[10px] font-bold uppercase text-zinc-500">EVIDENCE_LOGS</h3>
                  <DatasetList 
                    data={result.events.map((e: any) => `[${e.severity.toUpperCase()}] ${e.event_type} | IP:${e.src_ip} | ${e.description}`)}
                    title="ANALYSIS_EVIDENCE"
                    maxHeight="250px"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {currentPage === 'raw' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <h2 className="text-xl font-bold uppercase text-white">RAW_LOG_DATASET</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-1 border border-zinc-900 p-4 space-y-1 max-h-[300px] overflow-auto">
                <h4 className="text-[10px] font-bold text-zinc-500 mb-2 uppercase">Files</h4>
                {rawFiles.map(f => (
                  <button 
                    key={f} 
                    onClick={() => fetchRawPreview(f)}
                    className={`w-full text-left p-2 text-[10px] border truncate transition-all ${selectedRawFile === f ? 'bg-zinc-100 text-black border-zinc-100' : 'border-zinc-900 text-zinc-600 hover:border-zinc-700'}`}
                  >
                    {f}
                  </button>
                ))}
              </div>
              <div className="md:col-span-2">
                <DatasetList 
                  data={rawPreview ? rawPreview.split('\n') : []}
                  title="PREVIEW_CONTENT"
                  subtitle={selectedRawFile || 'NONE'}
                />
              </div>
            </div>
          </div>
        )}

        {currentPage === 'final' && (
          <div className="max-w-4xl mx-auto space-y-6">
            <h2 className="text-xl font-bold uppercase text-white">ENRICHED_EVENTS</h2>
            <DatasetList 
              data={finalEvents.map(e => `${e.event_type} | SEV:${e.severity} | IP:${e.src_ip} | ${e.description}`)}
              title="FULL_EVENT_DATASET"
            />
          </div>
        )}

        {currentPage === 'architecture' && (
          <div className="max-w-5xl mx-auto space-y-16 py-10">
            <header className="space-y-4 border-b border-zinc-900 pb-10">
              <h1 className="text-4xl font-black tracking-tighter text-white uppercase italic">SYSTEM_CORE</h1>
              <p className="text-zinc-500 text-xs tracking-[0.3em] uppercase">Deep Dive into ThreatLens Architecture</p>
            </header>

            {/* Section 1: Cloud */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div className="space-y-6">
                <div className="flex items-center gap-4">
                  <span className="text-3xl font-black text-zinc-800">01</span>
                  <h2 className="text-xl font-bold uppercase text-white tracking-tight">Cloud_Infrastructure</h2>
                </div>
                <div className="space-y-4 text-xs leading-relaxed text-zinc-400 font-sans">
                  <p>
                    The foundation of ThreatLens is built on authentic AWS telemetry. We deployed a custom VPC environment featuring EC2 instances running NGINX and public endpoints to simulate a production surface.
                  </p>
                  <p>
                    <span className="text-zinc-200 font-bold italic">VPC Flow Logs</span> are captured at 1-minute intervals and aggregated in S3. To ensure high-signal data, we developed traffic injection scripts that simulate both normal user patterns and sophisticated attack vectors including coordinated SSH brute-forcing and stealthy port reconnaissance.
                  </p>
                  <ul className="space-y-2 pt-4">
                    <li className="flex items-start gap-2">
                      <span className="text-zinc-100 mt-1">▪</span>
                      <span>Real-world traffic de-provisioned for secure analysis.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-zinc-100 mt-1">▪</span>
                      <span>JSONL normalization for high-performance parsing.</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="border border-zinc-900 p-2 bg-zinc-950/50 group overflow-hidden">
                <img src={cloudArch} alt="Cloud Architecture" className="w-full grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700 ease-in-out" />
                <div className="mt-2 text-[9px] text-zinc-700 font-mono text-center uppercase tracking-widest">Fig 01 // AWS_TELEMETRY_PLANE</div>
              </div>
            </div>

            {/* Section 2: System Logic */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div className="order-2 md:order-1 border border-zinc-900 p-2 bg-zinc-950/50 group overflow-hidden">
                <img src={systemArch} alt="System Architecture" className="w-full grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700 ease-in-out" />
                <div className="mt-2 text-[9px] text-zinc-700 font-mono text-center uppercase tracking-widest">Fig 02 // AGENTIC_RAG_PIPELINE</div>
              </div>
              <div className="order-1 md:order-2 space-y-6">
                <div className="flex items-center gap-4">
                  <span className="text-3xl font-black text-zinc-800">02</span>
                  <h2 className="text-xl font-bold uppercase text-white tracking-tight">Intelligence_Engine</h2>
                </div>
                <div className="space-y-4 text-xs leading-relaxed text-zinc-400 font-sans">
                  <p>
                    The transition from raw bytes to security intelligence happens through our <span className="text-zinc-200 font-bold">Window Analysis</span> engine. Instead of analyzing isolated packets, we correlate traffic in 60-second temporal windows.
                  </p>
                  <p>
                    Events are vectorized using <span className="text-zinc-200 font-bold italic">SentenceTransformers (all-MiniLM-L6-v2)</span> and stored in <span className="text-zinc-200 font-bold italic">ChromaDB</span>. This enables a Hybrid Retrieval strategy: Semantic search identifies intent-based matches, while structured metadata filters ensure temporal and severity precision.
                  </p>
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="border border-zinc-900 p-3 bg-black">
                      <div className="text-[10px] font-bold text-white uppercase mb-1">Vector_DB</div>
                      <div className="text-[9px] text-zinc-500 uppercase">ChromaDB Persistence</div>
                    </div>
                    <div className="border border-zinc-900 p-3 bg-black">
                      <div className="text-[10px] font-bold text-white uppercase mb-1">LLM_Core</div>
                      <div className="text-[9px] text-zinc-500 uppercase">GPT-4.1-mini Reasoning</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Engineering Specs */}
            <div className="border border-zinc-900 bg-zinc-950 p-8 space-y-6">
               <h3 className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.4em]">TECH_STACK_MANIFEST</h3>
               <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                  <div className="space-y-1">
                    <div className="text-white font-bold">FastAPI</div>
                    <div className="text-[9px] text-zinc-600 uppercase">Async Backend</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-white font-bold">SentenceTransformers</div>
                    <div className="text-[9px] text-zinc-600 uppercase">Embedding Layer</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-white font-bold">OpenRouter</div>
                    <div className="text-[9px] text-zinc-600 uppercase">LLM Orchestration</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-white font-bold">TypeScript</div>
                    <div className="text-[9px] text-zinc-600 uppercase">Strict Frontend</div>
                  </div>
               </div>
            </div>
          </div>
        )}

        {currentPage === 'about' && (
          <div className="max-w-xl mx-auto py-20 text-center space-y-6">
            <h2 className="text-3xl font-bold uppercase text-white tracking-widest">THREATLENS</h2>
            <p className="text-xs text-zinc-500 leading-relaxed uppercase">
                Bridging the gap between raw logs and actionable security intelligence.
            </p>
            <div className="flex justify-center gap-8 pt-10">
                <a href="https://vpjoshi.in" className="text-[10px] font-bold border-b border-zinc-800 hover:text-white transition-all uppercase">Portfolio</a>
                <a href="https://github.com/Joshi-labs/VPCThreatLens" className="text-[10px] font-bold border-b border-zinc-800 hover:text-white transition-all uppercase">Source</a>
            </div>
            <p className="text-[9px] text-zinc-800 pt-20">V.P.JOSHI // SOC_ENGINE_V1</p>
          </div>
        )}
      </main>

      <footer className="border-t border-zinc-900 py-6 mt-20">
        <div className="container mx-auto px-6 text-center text-[9px] font-bold uppercase tracking-widest text-zinc-700">
          VPC_THREATLENS // 2026 // END_TRANSMISSION
        </div>
      </footer>
    </div>
  );
}

export default App;
