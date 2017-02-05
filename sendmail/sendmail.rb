require 'csv'
require 'mail'
require 'dotenv'

Dotenv.load

from = 'Neutrinet <support@neutrinet.be>'
subject = 'A test email from ruby'
body_template = File.read('body.txt')

Mail.defaults do
  delivery_method :smtp, {
    address: ENV['SMTP_SERVER'],
    port: ENV['SMTP_PORT'],
    domain: ENV['SMTP_DOMAIN'],
    user_name: ENV['SMTP_USERNAME'],
    password: ENV['SMTP_PASSWORD'],
    authentication: :plain,
    ssl: true,
    tls: true
  }
end

def personalize_body(body, ip)
  body.gsub(/IP_ADDRESS/, ip)
end

def send_email(from, to, subject, body)
  mail = Mail.new do
    from    from
    to      to
    subject subject
    body    body
  end
  mail.deliver!
  puts "Sent to #{to}"
end

CSV.foreach("source.csv") do |row|
  to = row[0].strip
  ip = row[1].strip
  body = personalize_body(body_template, ip)
  send_email(from, to, subject, body)
  puts "Waiting before sending next email..."
  sleep(2)
end
