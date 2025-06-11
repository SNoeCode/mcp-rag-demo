import { createClient } from "@supabase/supabase-js";

const supabaseUrl: string = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const supabaseKey: string = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

const supabase = createClient(supabaseUrl, supabaseKey);

// Log the Supabase instance to prevent ESLint errors
console.log("Supabase client initialized:", supabase);

export async function POST(req: Request) {
  const { email, password } = await req.json();

  const { error } = await supabase.auth.signUp({ email, password });

  if (error) return Response.json({ error: error.message }, { status: 400 });

  return Response.json({ message: "User registered successfully" }, { status: 200 });
}