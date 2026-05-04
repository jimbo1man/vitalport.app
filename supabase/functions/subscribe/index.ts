import { createClient } from "jsr:@supabase/supabase-js@2";
import { Resend } from "npm:resend@4";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  let email: string;
  let source: string = "hero";

  try {
    const body = await req.json();
    email = (body.email ?? "").trim().toLowerCase();
    if (body.source) source = body.source;
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response(JSON.stringify({ error: "Valid email required" }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  );

  const { data, error: dbError } = await supabase
    .from("waitlist")
    .insert({ email, source })
    .select("id, created_at")
    .single();

  if (dbError) {
    // Unique constraint violation: already signed up
    if (dbError.code === "23505") {
      return new Response(JSON.stringify({ success: true, duplicate: true }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
    console.error("DB error:", dbError);
    return new Response(JSON.stringify({ error: "Failed to save email" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  const resend = new Resend(Deno.env.get("RESEND_API_KEY")!);

  // Fire both emails without blocking the response
  const fromDomain = Deno.env.get("FROM_DOMAIN") ?? "vitalport.app";
  const adminEmail = Deno.env.get("ADMIN_EMAIL") ?? `hello@${fromDomain}`;

  const emailJobs = [
    resend.emails.send({
      from: `Vitalport <hello@${fromDomain}>`,
      to: email,
      subject: "You're on the list.",
      text: "You'll be the first to know when Vitalport launches on the App Store.\n\nThanks for your interest.\n\n- The Vitalport Team",
    }),
    resend.emails.send({
      from: `notifications@${fromDomain}`,
      to: adminEmail,
      subject: "New Vitalport waitlist signup",
      text: `Email: ${email}\nSource: ${source}\nSigned up: ${data.created_at}`,
    }),
  ];

  Promise.allSettled(emailJobs).then((results) => {
    results.forEach((r, i) => {
      if (r.status === "rejected") console.error(`Email ${i} failed:`, r.reason);
    });
  });

  return new Response(JSON.stringify({ success: true }), {
    status: 200,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
});
