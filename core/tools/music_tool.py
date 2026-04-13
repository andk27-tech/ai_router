#!/usr/bin/env python3
"""
Music Tool Module
음악 툴 - YouTube 음악 검색 및 재생 (yt-dlp 사용)
"""

import yt_dlp
import subprocess
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MusicTrack:
    """음악 트랙 데이터 클래스"""
    title: str
    url: str
    duration: int
    uploader: str
    thumbnail: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None


class MusicTool:
    """음악 툴 클래스"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'default_search': 'ytsearch5',  # 검색 결과 5개
        }
    
    def search_music(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        YouTube 음악 검색
        
        Args:
            query: 검색어
            limit: 검색 결과 수
            
        Returns:
            검색 결과
        """
        try:
            opts = self.ydl_opts.copy()
            opts['default_search'] = f'ytsearch{limit}'
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                results = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            
            tracks = []
            if 'entries' in results:
                for entry in results['entries']:
                    track = MusicTrack(
                        title=entry.get('title', 'Unknown'),
                        url=entry.get('url', ''),
                        duration=entry.get('duration', 0),
                        uploader=entry.get('uploader', 'Unknown'),
                        thumbnail=entry.get('thumbnail'),
                        view_count=entry.get('view_count'),
                        upload_date=entry.get('upload_date')
                    )
                    tracks.append(track)
            
            return {
                'success': True,
                'query': query,
                'tracks': [
                    {
                        'title': track.title,
                        'url': track.url,
                        'duration': track.duration,
                        'uploader': track.uploader,
                        'thumbnail': track.thumbnail,
                        'view_count': track.view_count,
                        'upload_date': track.upload_date
                    }
                    for track in tracks
                ],
                'count': len(tracks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    def play_music(self, url: str, audio_only: bool = True) -> Dict[str, Any]:
        """
        음악 재생
        
        Args:
            url: YouTube URL
            audio_only: 오디오만 재생 여부
            
        Returns:
            재생 결과
        """
        try:
            # ffplay 또는 mpv 사용
            player = self._find_player()
            if not player:
                return {
                    'success': False,
                    'error': '오디오 플레이어를 찾을 수 없습니다 (ffplay 또는 mpv 필요)'
                }
            
            # yt-dlp로 오디오 스트림 가져오기
            opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info.get('url')
            
            if not audio_url:
                return {
                    'success': False,
                    'error': '오디오 URL을 가져올 수 없습니다'
                }
            
            # 플레이어로 재생
            cmd = [player, audio_url]
            
            # 백그라운드에서 실행
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            return {
                'success': True,
                'message': '음악 재생 중...',
                'player': player,
                'url': audio_url,
                'pid': process.pid
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_player(self) -> Optional[str]:
        """오디오 플레이어 찾기"""
        players = ['ffplay', 'mpv', 'vlc']
        for player in players:
            if subprocess.run(['which', player], capture_output=True).returncode == 0:
                return player
        return None
    
    def get_music_info(self, url: str) -> Dict[str, Any]:
        """
        음악 정보 가져오기
        
        Args:
            url: YouTube URL
            
        Returns:
            음악 정보
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            return {
                'success': True,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', '')[:500]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def search_music(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    음악 검색 편의 함수
    
    Args:
        query: 검색어
        limit: 검색 결과 수
        
    Returns:
        검색 결과
    """
    tool = MusicTool()
    return tool.search_music(query, limit)


def play_music(url: str) -> Dict[str, Any]:
    """
    음악 재생 편의 함수
    
    Args:
        url: YouTube URL
        
    Returns:
        재생 결과
    """
    tool = MusicTool()
    return tool.play_music(url)
