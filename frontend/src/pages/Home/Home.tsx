import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Home.module.css'; // Или используйте ваш CSS-файл

const Home: React.FC = () => {
  return (
    <div className={styles.container}>
      <h1>Добро пожаловать в конструктор форм</h1>
      <p>Создавайте и управляйте своими анкетами и опросами</p>
      
      <div className={styles.actions}>
        <Link to="/create-form" className={styles.button}>
          Создать новую форму
        </Link>
      </div>

      <section className={styles.features}>
        <h2>Возможности:</h2>
        <ul>
          <li>Создание форм с различными типами вопросов</li>
          <li>Просмотр и управление созданными формами</li>
          <li>Анализ ответов</li>
        </ul>
      </section>
    </div>
  );
};

export default Home;