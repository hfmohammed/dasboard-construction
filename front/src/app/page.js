"use client";
import Link from "next/link";
import React, { useState } from 'react';

import DashboardPage from '@/components/dashboard-page';
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/login-card";
import { Label } from "@/components/ui/login-label";
import { Input } from "@/components/ui/login-input";
import { Button } from "@/components/ui/login-button";

export default function Home() {
  const [loggedIn, setLoggedIn] = useState(false);

  const connect = async () => {
    console.log("connecting")
    try {
      const response = await fetch(`http://44.202.72.110:5001/start-server`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Network response was not ok.');
      }
    } catch (error) {
      console.error('Error starting server:', error);
    }
  }

  connect();

  const handleLogin = async () => {
    // Here you would typically check the credentials, 
    // but for this example, we'll just set loggedIn to true

    // Send a request to the backend to start the server
    setLoggedIn(true);

  };

  return (
    <React.StrictMode>
      {/* {loggedIn ? ( */}
      {1 ? (
        <>
          <Header />
          <DashboardPage />
          <Footer />
        </>
      ) : (
        <LoginPage onLogin={handleLogin} />
      )}
    </React.StrictMode>
  );
}

function LoginPage({ onLogin }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background">
      <header className="mb-8">
        <Link href="#" className="flex items-center gap-2" prefetch={false}>
          <MountainIcon className="h-6 w-6 text-primary" />
          <span className="font-bold text-2xl text-foreground">Acme Inc</span>
        </Link>
      </header>
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>Enter your credentials to access your account</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="username">Username</Label>
            <Input id="username" placeholder="Enter your username" />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" placeholder="Enter your password" />
          </div>
        </CardContent>
        <CardFooter className="pt-2">
          <Button type="submit" className="w-full bg-gray-800 text-white hover:bg-gray-600" onClick={onLogin}>
            Sign In
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

function MountainIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round">
      <path d="m8 3 4 8 5-5 5 15H2L8 3z" />
    </svg>
  );
}
