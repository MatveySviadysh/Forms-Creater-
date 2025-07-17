import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Добро пожаловать на мой сайт!</h1>
      </header>
      
      <main>
        <section className="intro">
          <h2>Обо мне</h2>
          <p>Привет! Меня зовут [Ваше имя], и это мой персональный сайт.</p>
        </section>
        
        <section className="projects">
          <h2>Мои проекты</h2>
          <div className="project-list">
            <div className="project-card">
              <h3>Проект 1</h3>
              <p>Описание первого проекта</p>
            </div>
            <div className="project-card">
              <h3>Проект 2</h3>
              <p>Описание второго проекта</p>
            </div>
          </div>
        </section>
      </main>
      
      <footer>
        <p>© {new Date().getFullYear()} Мой сайт. Все права защищены.</p>
      </footer>
    </div>
  );
}

export default App;