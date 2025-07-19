import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './styles.module.css';

type QuestionType = 'text' | 'radio' | 'checkbox' | 'dropdown';

interface Question {
  id: string;
  title: string;
  type: QuestionType;
  required: boolean;
  options?: { id: string; value: string }[];
}

const CreateForm: React.FC = () => {
  const navigate = useNavigate();
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [questions, setQuestions] = useState<Question[]>([]);

  const addQuestion = () => {
    setQuestions([
      ...questions,
      {
        id: Date.now().toString(),
        title: '',
        type: 'text',
        required: false
      }
    ]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/forms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: formTitle,
          description: formDescription,
          questions
        })
      });

      if (response.ok) {
        alert('Форма успешно создана!');
        navigate('/');
      } else {
        throw new Error('Ошибка при создании формы');
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Произошла ошибка при сохранении формы');
    }
  };

  return (
    <div className={styles.container}>
      <h1>Создание новой формы</h1>
      
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label>Название формы:</label>
          <input
            type="text"
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
            required
          />
        </div>

        <div className={styles.formGroup}>
          <label>Описание формы:</label>
          <textarea
            value={formDescription}
            onChange={(e) => setFormDescription(e.target.value)}
          />
        </div>

        <div className={styles.questions}>
          {questions.map((question, index) => (
            <div key={question.id} className={styles.question}>
              <h3>Вопрос {index + 1}</h3>
              {/* Здесь будет управление вопросами */}
            </div>
          ))}
        </div>

        <div className={styles.buttons}>
          <button type="button" onClick={addQuestion}>
            Добавить вопрос
          </button>
          <button type="submit">Сохранить форму</button>
        </div>
      </form>
    </div>
  );
};

export default CreateForm;