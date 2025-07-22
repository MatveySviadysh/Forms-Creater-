import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './styles.module.css';

type QuestionType = 'text' | 'radio' | 'checkbox' | 'dropdown' | 'linear_scale';

interface QuestionOption {
  id: string;
  value: string;
}

interface FormQuestion {
  id: string;
  title: string;
  type: QuestionType;
  required: boolean;
  options?: QuestionOption[];
  min_value?: number;
  max_value?: number;
  min_label?: string;
  max_label?: string;
}

const CreateForm: React.FC = () => {
  const navigate = useNavigate();
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [questions, setQuestions] = useState<FormQuestion[]>([]);

  const addQuestion = () => {
    setQuestions([
      ...questions,
      {
        id: Date.now().toString(),
        title: '',
        type: 'text',
        required: false,
        options: []
      }
    ]);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const updateQuestion = (index: number, field: keyof FormQuestion, value: any) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = {
      ...updatedQuestions[index],
      [field]: value
    };
    setQuestions(updatedQuestions);
  };

  const addOption = (questionIndex: number) => {
    const updatedQuestions = [...questions];
    updatedQuestions[questionIndex].options = [
      ...(updatedQuestions[questionIndex].options || []),
      { id: Date.now().toString(), value: '' }
    ];
    setQuestions(updatedQuestions);
  };

  const removeOption = (questionIndex: number, optionIndex: number) => {
    const updatedQuestions = [...questions];
    updatedQuestions[questionIndex].options = 
      updatedQuestions[questionIndex].options?.filter((_, i) => i !== optionIndex);
    setQuestions(updatedQuestions);
  };

  const updateOption = (questionIndex: number, optionIndex: number, value: string) => {
    const updatedQuestions = [...questions];
    if (updatedQuestions[questionIndex].options) {
      updatedQuestions[questionIndex].options![optionIndex].value = value;
      setQuestions(updatedQuestions);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/forms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: formTitle,
          description: formDescription,
          questions: questions.map(q => ({
            ...q,
            // Для linear_scale добавляем дополнительные поля
            ...(q.type === 'linear_scale' && {
              min_value: q.min_value || 1,
              max_value: q.max_value || 5,
              min_label: q.min_label || 'Min',
              max_label: q.max_label || 'Max'
            }),
            // Удаляем options для text типа
            options: q.type === 'text' ? undefined : q.options
          }))
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        alert(`Форма успешно создана! ID: ${data.id}`);
        navigate('/');
      } else {
        throw new Error(data.detail || 'Ошибка при создании формы');
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert(error instanceof Error ? error.message : 'Произошла ошибка при сохранении формы');
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
          {questions.map((question, qIndex) => (
            <div key={question.id} className={styles.question}>
              <h3>Вопрос {qIndex + 1}</h3>
              
              <div className={styles.formGroup}>
                <label>Текст вопроса:</label>
                <input
                  type="text"
                  value={question.title}
                  onChange={(e) => updateQuestion(qIndex, 'title', e.target.value)}
                  required
                />
              </div>
              
              <div className={styles.formGroup}>
                <label>Тип вопроса:</label>
                <select
                  value={question.type}
                  onChange={(e) => updateQuestion(qIndex, 'type', e.target.value as QuestionType)}
                >
                  <option value="text">Текстовый ответ</option>
                  <option value="radio">Один вариант</option>
                  <option value="checkbox">Несколько вариантов</option>
                  <option value="dropdown">Выпадающий список</option>
                  <option value="linear_scale">Линейная шкала</option>
                </select>
              </div>
              
              <div className={styles.formGroup}>
                <label>
                  <input
                    type="checkbox"
                    checked={question.required}
                    onChange={(e) => updateQuestion(qIndex, 'required', e.target.checked)}
                  />
                  Обязательный вопрос
                </label>
              </div>
              
              {question.type === 'linear_scale' && (
                <>
                  <div className={styles.formGroup}>
                    <label>Минимальное значение:</label>
                    <input
                      type="number"
                      value={question.min_value || 1}
                      onChange={(e) => updateQuestion(qIndex, 'min_value', parseInt(e.target.value))}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Максимальное значение:</label>
                    <input
                      type="number"
                      value={question.max_value || 5}
                      onChange={(e) => updateQuestion(qIndex, 'max_value', parseInt(e.target.value))}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Подпись минимума:</label>
                    <input
                      type="text"
                      value={question.min_label || ''}
                      onChange={(e) => updateQuestion(qIndex, 'min_label', e.target.value)}
                    />
                  </div>
                  <div className={styles.formGroup}>
                    <label>Подпись максимума:</label>
                    <input
                      type="text"
                      value={question.max_label || ''}
                      onChange={(e) => updateQuestion(qIndex, 'max_label', e.target.value)}
                    />
                  </div>
                </>
              )}
              
              {(question.type === 'radio' || question.type === 'checkbox' || question.type === 'dropdown') && (
                <div className={styles.options}>
                  <h4>Варианты ответов:</h4>
                  {question.options?.map((option, oIndex) => (
                    <div key={option.id} className={styles.option}>
                      <input
                        type="text"
                        value={option.value}
                        onChange={(e) => updateOption(qIndex, oIndex, e.target.value)}
                        placeholder="Текст варианта"
                      />
                      <button
                        type="button"
                        onClick={() => removeOption(qIndex, oIndex)}
                        className={styles.removeButton}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => addOption(qIndex)}
                    className={styles.addButton}
                  >
                    + Добавить вариант
                  </button>
                </div>
              )}
              
              <button
                type="button"
                onClick={() => removeQuestion(qIndex)}
                className={styles.removeQuestionButton}
              >
                Удалить вопрос
              </button>
            </div>
          ))}
        </div>

        <div className={styles.buttons}>
          <button type="button" onClick={addQuestion} className={styles.addButton}>
            Добавить вопрос
          </button>
          <button type="submit" className={styles.submitButton}>
            Сохранить форму
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateForm;