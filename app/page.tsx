const featuredProjects = [
  {
    title: "Custom Dining Table",
    description: "Hand-finished walnut with a live-edge silhouette and built-in bench seating.",
    image:
      "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Bespoke Kitchen Joinery",
    description: "Flourishing oak cabinetry that blends warmth, storage, and everyday function.",
    image:
      "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Outdoor Grill Station",
    description: "Weather-ready cedar detailing designed for backyard gathering and entertaining.",
    image:
      "https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80",
  },
];

const auctionHighlights = [
  { title: "Rare Heirloom Bench", price: "$1,250", status: "Live bidding" },
  { title: "Handcrafted Coffee Table", price: "$890", status: "7 bids" },
  { title: "Custom Mantel Shelf", price: "$640", status: "Ends tonight" },
];

const communityStories = [
  "Live shop demos and seasonal woodworking workshops",
  "Client design consultations for custom residential builds",
  "A community library of finishing techniques and care tips",
];

export default function Home() {
  return (
    <div className="site-shell">
      <header className="topbar">
        <div className="container nav">
          <div className="brand-wrap">
            <div className="brand-mark">S</div>
            <div>
              <p className="brand-name">Squirrels</p>
              <p className="brand-subtitle">Custom Woodworking</p>
            </div>
          </div>

          <nav className="main-nav" aria-label="Main navigation">
            <a href="#home">Home</a>
            <a href="#gallery">Gallery</a>
            <a href="#auctions">Auctions</a>
            <a href="#community">Community</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
          </nav>

          <a className="button button-primary" href="#contact">
            Book a consult
          </a>
        </div>
      </header>

      <main>
        <section id="home" className="hero-section">
          <div className="container hero-grid">
            <div className="hero-copy">
              <p className="eyebrow">Crafted for everyday living</p>
              <h1>Beautiful woodwork built around how you live.</h1>
              <p className="lead">
                We design and build custom furniture, architectural millwork, and
                statement pieces that bring warmth, function, and lasting character
                to your space.
              </p>

              <div className="hero-actions">
                <a className="button button-primary" href="#gallery">
                  View our work
                </a>
                <a className="button button-secondary" href="#about">
                  Learn our story
                </a>
              </div>

              <ul className="mini-stats" aria-label="Company stats">
                <li>
                  <strong>18+</strong>
                  <span>Years building</span>
                </li>
                <li>
                  <strong>500+</strong>
                  <span>Projects delivered</span>
                </li>
                <li>
                  <strong>4.9/5</strong>
                  <span>Client rating</span>
                </li>
              </ul>
            </div>

            <div className="hero-visual" aria-label="Featured woodworking project photo">
              <img
                src="https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=1200&q=80"
                alt="Warm wood dining room interior"
              />
              <div className="floating-card">
                <span>Featured build</span>
                <strong>Moss &amp; Maple Dining Set</strong>
              </div>
            </div>
          </div>
        </section>

        <section id="gallery" className="content-section">
          <div className="container">
            <div className="section-heading">
              <p className="eyebrow">Featured projects</p>
              <h2>Timeless craftsmanship in every detail.</h2>
            </div>

            <div className="project-grid">
              {featuredProjects.map((project) => (
                <article key={project.title} className="project-card">
                  <img src={project.image} alt={project.title} />
                  <div className="project-body">
                    <h3>{project.title}</h3>
                    <p>{project.description}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="auctions" className="content-section alt-section">
          <div className="container">
            <div className="section-heading split-heading">
              <div>
                <p className="eyebrow">Marketplace</p>
                <h2>Current auctions &amp; featured finds.</h2>
              </div>
              <a className="text-link" href="#contact">
                Request a custom piece
              </a>
            </div>

            <div className="auction-grid">
              {auctionHighlights.map((item) => (
                <article key={item.title} className="auction-card">
                  <p className="auction-label">{item.status}</p>
                  <h3>{item.title}</h3>
                  <div className="auction-meta">
                    <span>Current bid</span>
                    <strong>{item.price}</strong>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="community" className="content-section">
          <div className="container community-layout">
            <div className="community-copy">
              <p className="eyebrow">Community</p>
              <h2>Learn, gather, and create with us.</h2>
              <p>
                From family-friendly maker nights to finishing demos and learning
                sessions, we believe woodworking is best when shared.
              </p>
            </div>

            <ul className="community-list">
              {communityStories.map((story) => (
                <li key={story}>{story}</li>
              ))}
            </ul>
          </div>
        </section>

        <section id="about" className="content-section alt-section">
          <div className="container about-grid">
            <div className="about-panel">
              <p className="eyebrow">Our story</p>
              <h2>Built from a lifelong love of wood.</h2>
              <p>
                Squirrels Custom Woodworking started with a small neighborhood shop and
                a commitment to craftsmanship that feels personal. Every project is made
                with careful material selection, practical design, and attention to the
                way people actually live with their spaces.
              </p>
            </div>

            <div className="about-points">
              <div>
                <strong>Materials</strong>
                <span>Domestic hardwoods, reclaimed stock, beautiful finishes.</span>
              </div>
              <div>
                <strong>Process</strong>
                <span>Thoughtful design, precise execution, and reliable delivery.</span>
              </div>
              <div>
                <strong>Approach</strong>
                <span>Custom pieces tailored to your home, workflow, and style.</span>
              </div>
            </div>
          </div>
        </section>

        <section id="contact" className="content-section contact-section">
          <div className="container contact-grid">
            <div>
              <p className="eyebrow">Let&apos;s talk</p>
              <h2>Start your custom woodworking project.</h2>
              <p>
                Tell us what you&apos;re dreaming up and we&apos;ll help shape a practical,
                durable, custom-made result.
              </p>
              <ul className="contact-list">
                <li>(555) 234-1188</li>
                <li>hello@squirrelswoodworking.com</li>
                <li>124 Alder Street, Asheville, NC</li>
              </ul>
            </div>

            <form className="contact-card">
              <label>
                Name
                <input type="text" placeholder="Your name" />
              </label>
              <label>
                Email
                <input type="email" placeholder="you@example.com" />
              </label>
              <label>
                Project details
                <textarea rows={5} placeholder="Tell us about your room, style, and vision." />
              </label>
              <button type="submit" className="button button-primary full-width">
                Send inquiry
              </button>
            </form>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-row">
          <p>© 2025 Squirrels Custom Woodworking</p>
          <div className="footer-links">
            <a href="#gallery">Gallery</a>
            <a href="#community">Community</a>
            <a href="#contact">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
